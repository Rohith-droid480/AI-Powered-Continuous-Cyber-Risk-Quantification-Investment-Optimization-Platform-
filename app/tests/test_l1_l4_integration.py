import math
from pathlib import Path
import pytest
import numpy as np

from app.ingestion.parser import parse_nessus_xml, NessusParsingError
from app.enrichment.enrichment import enrich_vulnerabilities
from app.enrichment.seed_cves import seed_database
from app.enrichment.db import init_db
from app.risk.calibration import calibrate_vulnerability_risk
from app.simulation.engine import run_monte_carlo_simulation
from app.schemas.models import (
    ParsedVulnerability,
    EnrichedVulnerability,
    CalibratedRiskRecord,
    SimulationResults,
    EnrichmentStatus,
)

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "sample-data"


@pytest.fixture(autouse=True, scope="module")
def setup_local_database():
    """Ensures local database is seeded with CVE records before running integration tests."""
    init_db()
    seed_database()


def test_layer1_to_layer4_vertical_integration():
    """
    Vertical Integration Checkpoint Test (Layers 1 -> 4):
    Proves that a real .nessus scan flows through the entire object pipeline:
    REAL .nessus -> Layer 1 -> Layer 2 -> Layer 3 -> Layer 4 -> SimulationResults
    using the actual model contracts at each stage.
    """
    scan_file = SAMPLE_DATA_DIR / "enterprise_perimeter_scan.nessus"
    assert scan_file.exists(), f"Sample scan file not found: {scan_file}"

    with open(scan_file, "rb") as f:
        file_bytes = f.read()

    # Stage 1: Layer 1 Ingestion / Parsing
    parsed_vulns = parse_nessus_xml(file_bytes)
    assert isinstance(parsed_vulns, list)
    assert len(parsed_vulns) > 0, "Layer 1 produced zero vulnerabilities."
    assert len(parsed_vulns) == 5, f"Expected 5 findings, got {len(parsed_vulns)}"
    assert all(isinstance(v, ParsedVulnerability) for v in parsed_vulns)

    cve_ids = [v.cve_id for v in parsed_vulns]
    assert "CVE-2021-44228" in cve_ids
    assert "CVE-2020-1472" in cve_ids

    # Stage 2: Layer 2 Local Enrichment
    enriched_vulns = enrich_vulnerabilities(parsed_vulns)
    assert isinstance(enriched_vulns, list)
    assert len(enriched_vulns) == len(parsed_vulns)
    assert all(isinstance(ev, EnrichedVulnerability) for ev in enriched_vulns)

    # Confirm local database was consulted
    full_enrichments = [ev for ev in enriched_vulns if ev.enrichment_status == EnrichmentStatus.FULL]
    assert len(full_enrichments) > 0, "No vulnerabilities were enriched from local CVE database."

    log4j_ev = next(ev for ev in enriched_vulns if ev.cve_id == "CVE-2021-44228")
    assert log4j_ev.cvss_score == 10.0
    assert log4j_ev.epss_score == 0.97
    assert log4j_ev.is_kev is True

    # Stage 3: Layer 3 Risk Calibration
    calibrated_records = [calibrate_vulnerability_risk(ev) for ev in enriched_vulns]
    assert len(calibrated_records) == len(enriched_vulns)
    assert all(isinstance(r, CalibratedRiskRecord) for r in calibrated_records)

    total_analytical_eal = 0.0
    total_lef = 0.0

    for rec in calibrated_records:
        assert rec.t_cap >= 0.0 and rec.t_cap <= 1.0
        assert rec.rs >= 0.0 and rec.rs <= 1.0
        assert rec.vuln > 0.0 and rec.vuln <= 1.0
        assert rec.lef > 0.0
        assert rec.expected_primary_loss == 255_000_000.0
        assert math.isclose(rec.expected_secondary_loss, 0.4 * rec.expected_primary_loss, abs_tol=1e-5)
        assert math.isclose(rec.expected_loss_magnitude, 1.4 * rec.expected_primary_loss, abs_tol=1e-5)

        analytical_rec_eal = rec.lef * rec.expected_loss_magnitude
        total_analytical_eal += analytical_rec_eal
        total_lef += rec.lef

    # Stage 4: Layer 4 Vectorized Monte Carlo Simulation
    sim_results, job_error = run_monte_carlo_simulation(
        risk_records=calibrated_records,
        num_iterations=100_000,
        job_id="integration_test_job_001",
        seed=42,
    )

    assert job_error is None, f"Monte Carlo simulation failed: {job_error}"
    assert isinstance(sim_results, SimulationResults)
    assert sim_results.job_id == "integration_test_job_001"

    # Verify distribution and risk metrics
    assert len(sim_results.loss_distribution) == 100_000
    assert sim_results.eal > 0.0 and np.isfinite(sim_results.eal)
    assert sim_results.var_95 > 0.0 and np.isfinite(sim_results.var_95)
    assert sim_results.cvar_95 >= sim_results.var_95 and np.isfinite(sim_results.cvar_95)

    # Verify per-CVE risk summaries inside SimulationResults
    assert len(sim_results.per_cve_risk) == len(calibrated_records)

    # Mathematical Consistency Verification (Analytical EAL vs Simulated EAL)
    diff_abs = abs(sim_results.eal - total_analytical_eal)
    relative_diff_pct = (diff_abs / total_analytical_eal) * 100.0

    # Sanity threshold ±5%
    assert relative_diff_pct <= 5.0, (
        f"Simulated EAL ({sim_results.eal:,.2f}) deviated from Analytical EAL "
        f"({total_analytical_eal:,.2f}) by {relative_diff_pct:.2f}%, exceeding 5% threshold."
    )


def test_malformed_nessus_scan_graceful_failure():
    """
    Proves that a corrupted/malformed .nessus scan fails gracefully at Layer 1
    by raising NessusParsingError without unhandled raw exceptions.
    """
    malformed_file = SAMPLE_DATA_DIR / "malformed_corrupt.nessus"
    assert malformed_file.exists(), f"Sample malformed scan file not found: {malformed_file}"

    with open(malformed_file, "rb") as f:
        file_bytes = f.read()

    with pytest.raises(NessusParsingError) as exc_info:
        parse_nessus_xml(file_bytes)

    assert "Failed to parse XML syntax" in str(exc_info.value)
