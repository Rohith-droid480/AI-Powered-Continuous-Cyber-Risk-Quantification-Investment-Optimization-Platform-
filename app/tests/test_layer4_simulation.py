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
