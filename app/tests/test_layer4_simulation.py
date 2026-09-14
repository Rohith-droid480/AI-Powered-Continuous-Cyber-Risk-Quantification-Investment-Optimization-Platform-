import pytest
import inspect
import numpy as np
from app.schemas.models import EnrichedVulnerability, EnrichmentStatus, JobStatusEnum
from app.risk.calibration import calibrate_vulnerability_risk
from app.simulation.engine import run_monte_carlo_simulation


def test_vectorization_requirement_code_inspection():
    """
    Code inspection test: Verifies that engine.py explicitly declares the vectorization
    requirement and does not contain a per-trial for-loop over num_iterations.
    """
    import app.simulation.engine as engine_module
    source = inspect.getsource(engine_module)
    assert "VECTORIZATION REQUIREMENT" in source, "Source missing VECTORIZATION REQUIREMENT declaration"
    assert "for i in range(num_iterations)" not in source, "Prohibited per-trial Python for-loop found"
    assert "RandomState" not in source, "Legacy RandomState found in simulation engine"


def test_layer4_single_vuln_primary_validation():
    """
    Primary Validation Test (Step 10):
    Input: Single vulnerability with LEF = 0.5 events/year, Layer 3 real calibrated parameters
    (mu ~ 18.5520, sigma ~ 1.2686), Expected Loss Magnitude = ₹357,000,000.
    Analytical EAL = 0.5 * ₹357,000,000 = ₹178,500,000.
    Assert simulated EAL with seed=42 falls within ±3% of ₹178,500,000.
    Actual simulated EAL achieved: ₹182,097,849.61 (diff +2.02%).
    """
    vuln = EnrichedVulnerability(
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
    
    rec = calibrate_vulnerability_risk(
        vulnerability=vuln,
        rs=0.5,
        base_contact_rate=1.5,
        exposure_factor=0.5,
        mean_primary_loss=255_000_000.0,
        cv_primary_loss=2.0
    )
    
    assert rec.lef == 0.5, f"Expected LEF of 0.5, got {rec.lef}"
    assert rec.expected_loss_magnitude == 357_000_000.0
    
    analytical_eal = 0.5 * 357_000_000.0  # ₹178,500,000
    
    results, err = run_monte_carlo_simulation([rec], num_iterations=100_000, seed=42)
    assert err is None
    assert results is not None
    
    simulated_eal = results.eal
    # Achieved simulated EAL: ₹182,097,849.61
    assert pytest.approx(simulated_eal, rel=0.03) == analytical_eal, (
        f"Simulated EAL ₹{simulated_eal:,.2f} outside ±3% tolerance of analytical ₹{analytical_eal:,.2f}"
    )


def test_layer4_multi_vulnerability_aggregation():
    """
    Multi-Vulnerability Aggregation Test (Step 11):
    Tests multiple vulnerabilities with distinct LEF, mu, and sigma values.
    Confirms aggregation reflects each vulnerability's own parameters rather than an averaged set.
    Analytical EAL = EAL_1 + EAL_2 = ₹178,500,000 + ₹13,998,427.59 = ₹192,498,427.59.
    Simulated EAL with seed 42 = ₹194,034,647.12 (diff +0.80%, well within ±3%).
    """
    v1 = EnrichedVulnerability(
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
    v2 = EnrichedVulnerability(
        cve_id="CVE-2023-38606",
        plugin_id="160000",
        plugin_name="Kernel Privilege Escalation",
        host="192.168.1.105",
        port=443,
        protocol="tcp",
        severity=3,
        description="Kernel vulnerability",
        cvss_score=7.8,
        epss_score=0.45,
        is_kev=False,
        enrichment_status=EnrichmentStatus.FULL
    )
    
    r1 = calibrate_vulnerability_risk(
        vulnerability=v1,
        rs=0.5,
        base_contact_rate=1.5,
        exposure_factor=0.5,
        mean_primary_loss=255_000_000.0,
        cv_primary_loss=2.0
    )
    r2 = calibrate_vulnerability_risk(
        vulnerability=v2,
        rs=0.5,
        base_contact_rate=0.4285714,
        exposure_factor=0.9850746,
        mean_primary_loss=50_000_000.0,
        cv_primary_loss=1.5
    )
    
    analytical_eal_1 = r1.lef * r1.expected_loss_magnitude
    analytical_eal_2 = r2.lef * r2.expected_loss_magnitude
    total_analytical_eal = analytical_eal_1 + analytical_eal_2
    
    results, err = run_monte_carlo_simulation([r1, r2], num_iterations=100_000, seed=42)
    assert err is None
    assert results is not None
    assert len(results.per_cve_risk) == 2
    
    # Assert distinct cve_ids and non-zero baseline EALs
    assert results.per_cve_risk[0].cve_id == "CVE-2021-44228"
    assert results.per_cve_risk[1].cve_id == "CVE-2023-38606"
    assert results.per_cve_risk[0].baseline_eal == analytical_eal_1
    assert pytest.approx(results.per_cve_risk[1].baseline_eal) == analytical_eal_2
    
    # Assert simulated EAL matches total analytical EAL within ±3%
    assert pytest.approx(results.eal, rel=0.03) == total_analytical_eal


def test_layer4_simulation_failed_state():
    """
    Failure State Test (Step 12):
    Verifies SIMULATION_FAILED JobStatus is returned on invalid inputs without crashing.
    """
    # Case A: Empty list
    results, err = run_monte_carlo_simulation([], num_iterations=100_000, job_id="job_empty")
    assert results is None
    assert err is not None
    assert err.status == JobStatusEnum.SIMULATION_FAILED
    assert "empty" in err.message.lower()
    
    # Case B: Negative LEF
    v_invalid = EnrichedVulnerability(
        cve_id="CVE-2021-44228", plugin_id="1", plugin_name="Bad", host="10.0.0.1", port=80, protocol="tcp",
        severity=4, description="Bad", cvss_score=10.0, epss_score=0.97, is_kev=True, enrichment_status=EnrichmentStatus.FULL
    )
    rec_invalid = calibrate_vulnerability_risk(v_invalid, rs=0.5, base_contact_rate=1.5, exposure_factor=0.5)
    rec_invalid.lef = -0.5  # Forced invalid LEF
    
    results, err = run_monte_carlo_simulation([rec_invalid], num_iterations=100_000, job_id="job_neg_lef")
    assert results is None
    assert err is not None
    assert err.status == JobStatusEnum.SIMULATION_FAILED
    assert "invalid record parameters" in err.message.lower()


def test_layer4_event_attribution_ratio():
    """
    Event Attribution Ratio Test (Step 2 refactor verification):
    Calls engine._simulate_events directly to observe the engine's real internal decision.
    - Setup: LEF_1 = 0.5, LEF_2 = 0.2, num_iterations = 100,000, seed = 42.
    - Expected ratio: LEF_1 : LEF_2 = 0.5 : 0.2 = 2.5000 (71.43% : 28.57%).
    - Actual internal counts: Vuln 1 = 50,123 (71.27%), Vuln 2 = 20,201 (28.73%), total events = 70,324.
    - Actual empirical ratio: 2.4812 (relative error 0.75%, well within ±5%).
    """
    from app.simulation.engine import _simulate_events
    
    v1 = EnrichedVulnerability(
        cve_id="CVE-2021-44228", plugin_id="1", plugin_name="Log4j", host="10.0.0.1", port=80, protocol="tcp",
        severity=4, description="Log4j", cvss_score=10.0, epss_score=0.97, is_kev=True, enrichment_status=EnrichmentStatus.FULL
    )
    v2 = EnrichedVulnerability(
        cve_id="CVE-2023-38606", plugin_id="2", plugin_name="Kernel", host="10.0.0.2", port=443, protocol="tcp",
        severity=3, description="Kernel", cvss_score=7.8, epss_score=0.45, is_kev=False, enrichment_status=EnrichmentStatus.FULL
    )
    
    r1 = calibrate_vulnerability_risk(v1, rs=0.5, base_contact_rate=1.5, exposure_factor=0.5, mean_primary_loss=255_000_000.0, cv_primary_loss=2.0)
    r2 = calibrate_vulnerability_risk(v2, rs=0.5, base_contact_rate=0.4285714, exposure_factor=0.9850746, mean_primary_loss=50_000_000.0, cv_primary_loss=1.5)
    
    rng = np.random.default_rng(42)
    sampled_vuln_indices, primary_losses, iteration_indices = _simulate_events(
        risk_records=[r1, r2],
        num_iterations=100_000,
        rng=rng,
    )
    
    total_events = len(sampled_vuln_indices)
    count_v1 = int(np.sum(sampled_vuln_indices == 0))
    count_v2 = int(np.sum(sampled_vuln_indices == 1))
    
    ratio_empirical = count_v1 / count_v2
    ratio_expected = 0.5 / 0.2
    
    assert total_events == 70324
    assert count_v1 == 50123
    assert count_v2 == 20201
    assert pytest.approx(ratio_empirical, rel=0.05) == ratio_expected


def test_generate_compact_lec_unit_and_edge_cases():
    """
    Unit test for backend generate_compact_lec helper:
    a. Known small loss distribution [0, 100, 200, 300] CCDF coordinates.
    b. Points count <= 200.
    c. Exceedance probabilities within [0.0, 100.0].
    d. Monotonically non-increasing exceedance probabilities.
    e. Empty distribution fail-soft behavior.
    """
    from app.simulation.engine import generate_compact_lec

    # a. Known small distribution
    small_dist = [0.0, 100.0, 200.0, 300.0]
    pts = generate_compact_lec(small_dist, max_points=10)
    assert len(pts) > 0
    assert pts[0]["loss"] == 0.0
    assert pts[0]["exceedance_probability"] == 100.0
    assert pts[1]["loss"] == 100.0
    assert pts[1]["exceedance_probability"] == 75.0

    # b. Points count <= 200 on large distribution
    large_dist = list(np.random.lognormal(mean=18.5, sigma=1.2, size=100_000))
    pts_large = generate_compact_lec(large_dist, max_points=100)
    assert len(pts_large) <= 200

    # c & d. Probabilities within [0, 100] and monotonically non-increasing
    probs = [p["exceedance_probability"] for p in pts_large]
    assert all(0.0 <= p <= 100.0 for p in probs)
    for i in range(len(probs) - 1):
        assert probs[i] >= probs[i + 1], f"Exceedance probability non-monotonic at index {i}: {probs[i]} < {probs[i+1]}"

    # e. Empty fail-soft
    assert generate_compact_lec([]) == []
    assert generate_compact_lec(None) == []





