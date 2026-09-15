import pytest
from pathlib import Path
from app.ingestion.parser import parse_nessus_xml
from app.enrichment.enrichment import enrich_vulnerabilities
from app.risk.calibration import calibrate_vulnerability_risk
from app.optimization.optimizer import calculate_patch_cost, optimize_patch_investments
from app.schemas.models import (
    ParsedVulnerability,
    EnrichedVulnerability,
    CalibratedRiskRecord,
    EnrichmentStatus,
    JobStatusEnum,
    OptimizationResults,
)

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "sample-data"


def _make_dummy_record(
    cve_id: str,
    cvss_score: float,
    lef: float,
    expected_loss_magnitude: float,
) -> CalibratedRiskRecord:
    """Helper factory for creating valid CalibratedRiskRecord fixtures."""
    exp_primary = expected_loss_magnitude / 1.4
    exp_secondary = 0.4 * exp_primary
    
    ev = EnrichedVulnerability(
        cve_id=cve_id,
        plugin_id="100001",
        plugin_name=f"Plugin for {cve_id}",
        host="10.0.0.1",
        port=80,
        protocol="tcp",
        severity=4 if cvss_score >= 9.0 else 3,
        description="Test vulnerability",
        cvss_score=cvss_score,
        epss_score=0.5,
        is_kev=False,
        enrichment_status=EnrichmentStatus.FULL,
    )
    
    return CalibratedRiskRecord(
        vulnerability=ev,
        t_cap=0.5,
        rs=0.5,
        vuln=0.5,
        tef=lef / 0.5,
        lef=lef,
        primary_loss_mu=18.55,
        primary_loss_sigma=1.26,
        expected_primary_loss=exp_primary,
        expected_secondary_loss=exp_secondary,
        expected_loss_magnitude=expected_loss_magnitude,
    )


def test_layer5_patch_cost_calculation_tiers():
    """
    TEST 1 — COST TIERS
    Verifies exact remediation costs for Critical, High, Medium, and Low CVSS tiers
    with hourly_rate = ₹2,000/hr.
    """
    rate = 2000.0

    # Critical tier
    assert calculate_patch_cost(10.0, rate) == 80000.0
    assert calculate_patch_cost(9.5, rate) == 80000.0
    assert calculate_patch_cost(9.0, rate) == 80000.0

    # High tier
    assert calculate_patch_cost(8.9, rate) == 32000.0
    assert calculate_patch_cost(7.5, rate) == 32000.0
    assert calculate_patch_cost(7.0, rate) == 32000.0

    # Medium tier
    assert calculate_patch_cost(6.9, rate) == 16000.0
    assert calculate_patch_cost(5.0, rate) == 16000.0
    assert calculate_patch_cost(4.0, rate) == 16000.0

    # Low tier
    assert calculate_patch_cost(3.9, rate) == 8000.0
    assert calculate_patch_cost(2.6, rate) == 8000.0
    assert calculate_patch_cost(0.0, rate) == 8000.0


def test_layer5_delta_eal_knapsack_optimization():
    """
    TEST 2 — ΔEAL OBJECTIVE / KNAPSACK
    Creates 3 toy vulnerabilities and verifies PuLP 0/1 Knapsack selection.
    """
    cve_a = _make_dummy_record("CVE-A", cvss_score=10.0, lef=0.5, expected_loss_magnitude=200_000_000.0) # cost=80k, EAL=100M
    cve_b = _make_dummy_record("CVE-B", cvss_score=8.0, lef=0.3, expected_loss_magnitude=200_000_000.0)  # cost=32k, EAL=60M
    cve_c = _make_dummy_record("CVE-C", cvss_score=5.0, lef=0.1, expected_loss_magnitude=200_000_000.0)  # cost=16k, EAL=20M

    records = [cve_a, cve_b, cve_c]
    budget = 96_000.0

    results, err = optimize_patch_investments(records, budget=budget, seed=42)

    assert err is None
    assert isinstance(results, OptimizationResults)
    assert results.selected_cves == ["CVE-A", "CVE-C"]
    assert results.total_cost == 96_000.0
    assert results.delta_eal_per_cve == {"CVE-A": 100_000_000.0, "CVE-C": 20_000_000.0}


def test_layer5_optimization_failure_states():
    """
    TEST 3 — FAILURE STATES
    Tests graceful failure handling for negative budget and empty input list.
    """
    cve_a = _make_dummy_record("CVE-A", cvss_score=10.0, lef=0.5, expected_loss_magnitude=200_000_000.0)

    # 1. Negative budget
    res, err = optimize_patch_investments([cve_a], budget=-5000.0)
    assert res is None
    assert err is not None
    assert err.status == JobStatusEnum.OPTIMIZATION_UNAVAILABLE
    assert "cannot be negative" in err.message

    # 2. Empty risk records
    res, err = optimize_patch_investments([], budget=50000.0)
    assert res is None
    assert err is not None
    assert err.status == JobStatusEnum.OPTIMIZATION_UNAVAILABLE
    assert "empty" in err.message


def test_layer5_post_optimization_resimulation():
    """
    TEST 4 — POST-OPTIMIZATION RE-SIMULATION
    Verifies that selected CVEs are removed from post-optimization Monte Carlo re-simulation.
    """
    cve_a = _make_dummy_record("CVE-A", cvss_score=10.0, lef=0.5, expected_loss_magnitude=200_000_000.0) # cost=80k
    cve_b = _make_dummy_record("CVE-B", cvss_score=5.0, lef=0.2, expected_loss_magnitude=100_000_000.0)  # cost=16k

    records = [cve_a, cve_b]
    budget = 20_000.0

    results, err = optimize_patch_investments(records, budget=budget, num_iterations=10_000, seed=42)

    assert err is None
    assert results.selected_cves == ["CVE-B"]
    assert results.total_cost == 16_000.0
    assert results.post_opt_eal > 0.0
    assert results.post_opt_var_95 > 0.0
    assert results.post_opt_cvar_95 >= results.post_opt_var_95


def test_layer5_objective_traceability_not_cvss():
    """
    TEST 5 — OBJECTIVE TRACEABILITY
    Proves that the optimizer selects CVE-HIGH-DEAL due to higher Delta EAL, ignoring higher CVSS severity.
    """
    cve_high_cvss = _make_dummy_record("CVE-HIGH-CVSS", cvss_score=10.0, lef=0.05, expected_loss_magnitude=200_000_000.0)
    cve_high_deal = _make_dummy_record("CVE-HIGH-DEAL", cvss_score=5.0, lef=0.50, expected_loss_magnitude=200_000_000.0)

    records = [cve_high_cvss, cve_high_deal]
    budget = 50_000.0

    results, err = optimize_patch_investments(records, budget=budget, seed=42)

    assert err is None
    assert results.selected_cves == ["CVE-HIGH-DEAL"]
    assert results.total_cost == 16_000.0
    assert "CVE-HIGH-CVSS" not in results.selected_cves


def test_layer5_real_data_integration():
    """
    TEST 6 — REAL DATA INTEGRATION
    Runs full Layer 1 -> Layer 2 -> Layer 3 -> Layer 5 optimization on enterprise_perimeter_scan.nessus.
    """
    scan_file = SAMPLE_DATA_DIR / "enterprise_perimeter_scan.nessus"
    assert scan_file.exists()

    with open(scan_file, "rb") as f:
        file_bytes = f.read()

    parsed = parse_nessus_xml(file_bytes)
    enriched = enrich_vulnerabilities(parsed)
    records = [calibrate_vulnerability_risk(e) for e in enriched]

    demo_budget = 150_000.0
    opt_res, opt_err = optimize_patch_investments(records, budget=demo_budget, seed=42)

    assert opt_err is None
    assert isinstance(opt_res, OptimizationResults)
    assert opt_res.budget == 150_000.0
    assert opt_res.total_cost <= demo_budget
    assert opt_res.total_cost == 120_000.0
    assert set(opt_res.selected_cves) == {"CVE-2008-5161", "CVE-2020-1472", "CVE-2021-41773"}
    assert opt_res.post_opt_eal > 0.0
    assert opt_res.post_opt_var_95 > 0.0
    assert opt_res.post_opt_cvar_95 >= opt_res.post_opt_var_95


def test_layer5_empty_remaining_records_zero_residual():
    """
    TEST 7 — EMPTY REMAINING SET (DELIBERATE BUSINESS RULE)
    Verifies that when all vulnerabilities are selected (budget >= total cost),
    the remaining records list is empty and post_opt_eal, post_opt_var_95, post_opt_cvar_95
    are explicitly returned as 0.0 without triggering SIMULATION_FAILED.
    """
    cve_a = _make_dummy_record("CVE-A", cvss_score=5.0, lef=0.2, expected_loss_magnitude=100_000_000.0) # cost=16k

    records = [cve_a]
    budget = 50_000.0  # Budget covers CVE-A

    results, err = optimize_patch_investments(records, budget=budget, seed=42)

    assert err is None
    assert results.selected_cves == ["CVE-A"]
    assert results.total_cost == 16_000.0
    assert results.post_opt_eal == 0.0
    assert results.post_opt_var_95 == 0.0
    assert results.post_opt_cvar_95 == 0.0

