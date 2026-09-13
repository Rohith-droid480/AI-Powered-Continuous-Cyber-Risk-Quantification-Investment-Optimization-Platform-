import pytest
from app.risk.calibration import calculate_tcap


def test_tcap_kev_true():
    """
    Test A - Input: KEV=True, EPSS=0.25 -> Expected TCap: 1.0
    """
    result = calculate_tcap(is_kev=True, epss_score=0.25)
    assert result == 1.0, f"Expected 1.0 for KEV=True, got {result}"


def test_tcap_kev_false():
    """
    Test B - Input: KEV=False, EPSS=0.25 -> Expected TCap: 0.25
    """
    result = calculate_tcap(is_kev=False, epss_score=0.25)
    assert result == 0.25, f"Expected 0.25 for KEV=False, got {result}"


def test_rs_baseline():
    """
    Test RS - Input RS: 0.5 -> Expected RS: 0.5
    """
    from app.risk.calibration import calculate_rs
    result = calculate_rs(0.5)
    assert result == 0.5, f"Expected RS of 0.5, got {result}"


def test_vuln_hand_computable():
    """
    Test Vuln - TCap=1.0, RS=0.5 -> Expected Vuln = 1.0 / (1.0 + 0.5) = 0.666666... approx 0.667
    """
    from app.risk.calibration import calculate_vuln
    result = calculate_vuln(t_cap=1.0, rs=0.5)
    assert pytest.approx(result, abs=1e-3) == 0.667, f"Expected approx 0.667, got {result}"


def test_tef_hand_computable():
    """
    Test TEF - Base contact rate = 2.0 events/year, exposure factor = 0.5 -> Expected TEF = 1.0 event/year
    """
    from app.risk.calibration import calculate_tef
    result = calculate_tef(base_contact_rate=2.0, exposure_factor=0.5)
    assert result == 1.0, f"Expected TEF of 1.0 event/year, got {result}"


def test_lef_hand_computable():
    """
    Test LEF - TEF = 1.0, Vuln = 0.5 -> Expected LEF = 1.0 * 0.5 = 0.5 loss events/year
    """
    from app.risk.calibration import calculate_lef
    result = calculate_lef(tef=1.0, vuln=0.5)
    assert result == 0.5, f"Expected LEF of 0.5 loss events/year, got {result}"


def test_primary_loss_hand_computable():
    """
    Test Primary Loss calibration using IBM India 2026 value mu_X = ₹255,000,000 and CV_X = 2.0.
    Expected LogNormal mu approx 18.5520, sigma approx 1.2686, expected primary loss ₹255,000,000.
    """
    from app.risk.calibration import calibrate_primary_loss
    mu, sigma, exp_loss = calibrate_primary_loss(mean_loss=255_000_000.0, cv_loss=2.0)
    assert pytest.approx(mu, abs=1e-3) == 18.5520, f"Expected mu approx 18.5520, got {mu}"
    assert pytest.approx(sigma, abs=1e-3) == 1.2686, f"Expected sigma approx 1.2686, got {sigma}"
    assert exp_loss == 255_000_000.0, f"Expected expected primary loss ₹255,000,000, got {exp_loss}"


def test_secondary_loss_hand_computable():
    """
    Test Secondary Loss - Primary Loss = ₹1,000,000, Secondary ratio = 0.4 -> Expected Secondary Loss = ₹400,000
    """
    from app.risk.calibration import calculate_secondary_loss
    result = calculate_secondary_loss(primary_loss=1_000_000.0, secondary_ratio=0.4)
    assert result == 400_000.0, f"Expected ₹400,000, got {result}"


def test_loss_magnitude_hand_computable():
    """
    Test Loss Magnitude - Primary Loss = ₹1,000,000, Secondary Loss = ₹400,000 -> Expected Loss Magnitude = ₹1,400,000
    """
    from app.risk.calibration import calculate_loss_magnitude
    result = calculate_loss_magnitude(primary_loss=1_000_000.0, secondary_loss=400_000.0)
    assert result == 1_400_000.0, f"Expected ₹1,400,000, got {result}"


def test_edge_case_rs_out_of_bounds():
    """
    Edge Case Test - Invalid RS bounds (< 0 or > 1) raise ValueError
    """
    from app.risk.calibration import calculate_rs
    with pytest.raises(ValueError, match="RS score must be between 0.0 and 1.0"):
        calculate_rs(-0.1)
    with pytest.raises(ValueError, match="RS score must be between 0.0 and 1.0"):
        calculate_rs(1.5)


def test_edge_case_vuln_zero_denominator():
    """
    Edge Case Test - Denominator (TCap + RS) <= 0 raises ValueError
    """
    from app.risk.calibration import calculate_vuln
    with pytest.raises(ValueError, match="Denominator \\(TCap \\+ RS\\) must be greater than 0"):
        calculate_vuln(t_cap=0.0, rs=0.0)


def test_full_risk_calibration_pipeline_schema():
    """
    Pipeline Test - Verify calibrate_vulnerability_risk returns valid CalibratedRiskRecord
    matching Pydantic contract exactly.
    """
    from app.schemas.models import EnrichedVulnerability, EnrichmentStatus, CalibratedRiskRecord
    from app.risk.calibration import calibrate_vulnerability_risk
    
    vuln_input = EnrichedVulnerability(
        cve_id="CVE-2021-44228",
        plugin_id="155998",
        plugin_name="Apache Log4j RCE",
        host="192.168.1.100",
        port=8080,
        protocol="tcp",
        severity=4,
        description="Log4j remote code execution vulnerability",
        cvss_score=10.0,
        epss_score=0.97,
        is_kev=True,
        enrichment_status=EnrichmentStatus.FULL
    )
    
    record = calibrate_vulnerability_risk(
        vulnerability=vuln_input,
        rs=0.5,
        base_contact_rate=2.0,
        exposure_factor=0.5,
        mean_primary_loss=255_000_000.0,
        cv_primary_loss=2.0
    )
    
    assert isinstance(record, CalibratedRiskRecord)
    assert record.vulnerability.cve_id == "CVE-2021-44228"
    assert record.t_cap == 1.0
    assert record.rs == 0.5
    assert pytest.approx(record.vuln, abs=1e-3) == 0.667
    assert record.tef == 1.0
    assert pytest.approx(record.lef, abs=1e-3) == 0.667
    assert pytest.approx(record.primary_loss_mu, abs=1e-3) == 18.5520
    assert pytest.approx(record.primary_loss_sigma, abs=1e-3) == 1.2686
    assert record.expected_primary_loss == 255_000_000.0
    assert record.expected_secondary_loss == 102_000_000.0
    assert record.expected_loss_magnitude == 357_000_000.0








