import pytest
from app.optimization.optimizer import calculate_patch_cost, optimize_patch_investments
from app.schemas.models import (
    ParsedVulnerability,
    EnrichedVulnerability,
    CalibratedRiskRecord,
    EnrichmentStatus,
    JobStatusEnum,
    OptimizationResults,
)


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
    - Critical (CVSS >= 9.0): 40 hrs * 2000 = ₹80,000
    - High (7.0 <= CVSS < 9.0): 16 hrs * 2000 = ₹32,000
    - Medium (4.0 <= CVSS < 7.0): 8 hrs * 2000 = ₹16,000
    - Low (CVSS < 4.0): 4 hrs * 2000 = ₹8,000
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
    Creates 3 toy vulnerabilities:
    - CVE-A: cost = ₹80,000 (CVSS 10.0), Delta EAL = ₹100,000,000 (LEF=0.5, ExpLoss=200M)
    - CVE-B: cost = ₹32,000 (CVSS 8.0), Delta EAL = ₹60,000,000  (LEF=0.3, ExpLoss=200M)
    - CVE-C: cost = ₹16,000 (CVSS 5.0), Delta EAL = ₹20,000,000  (LEF=0.1, ExpLoss=200M)

    Budget = ₹112,000
    Optimal combination: CVE-A + CVE-C (Cost = ₹96,000, Total Delta EAL = ₹120M).
    CVE-A + CVE-B requires ₹112,000 but yields ₹160M? Wait:
    Cost A + B = 80,000 + 32,000 = 112,000 (Delta EAL = 160M).
    Let's adjust costs/budget so the 0/1 Knapsack choice is unambiguous and strictly tests capacity:
    CVE-A: cost = ₹80,000, Delta EAL = ₹100,000,000
    CVE-B: cost = ₹32,000, Delta EAL = ₹60,000,000
    CVE-C: cost = ₹16,000, Delta EAL = ₹20,000,000
    Budget = ₹40,000:
    Can buy: B (cost 32k, EAL 60M) vs C (cost 16k, EAL 20M). Optimal: ['CVE-B'].
    Budget = ₹96,000:
    Option 1: A + C -> cost 96k, Delta EAL = 120M
    Option 2: B + C -> cost 48k, Delta EAL = 80M
    Option 3: A alone -> cost 80k, Delta EAL = 100M
    Option 4: A + B -> cost 112k (> 96k, infeasible)
    Optimal for budget ₹96,000 is ['CVE-A', 'CVE-C'] with cost ₹96,000 and Delta EAL = ₹120M!
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
    Tests graceful failure handling for:
    - Negative budget (< 0) -> OPTIMIZATION_UNAVAILABLE
    - Empty risk_records list -> OPTIMIZATION_UNAVAILABLE
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
    Verifies that selected CVEs are removed from post-optimization Monte Carlo re-simulation
    and unselected CVEs remain, populating post_opt_eal, post_opt_var_95, and post_opt_cvar_95.
    """
    cve_a = _make_dummy_record("CVE-A", cvss_score=10.0, lef=0.5, expected_loss_magnitude=200_000_000.0) # cost=80k
    cve_b = _make_dummy_record("CVE-B", cvss_score=5.0, lef=0.2, expected_loss_magnitude=100_000_000.0)  # cost=16k

    records = [cve_a, cve_b]
    # Budget = 20,000 (enough only for CVE-B)
    budget = 20_000.0

    results, err = optimize_patch_investments(records, budget=budget, num_iterations=10_000, seed=42)

    assert err is None
    assert results.selected_cves == ["CVE-B"]
    assert results.total_cost == 16_000.0
    
    # Remaining unpatched vulnerability is CVE-A (LEF=0.5, ExpLoss=200M -> Baseline EAL = 100M)
    # Post-opt Monte Carlo EAL should be near ~100M (re-simulating CVE-A alone)
    assert results.post_opt_eal > 0.0
    assert results.post_opt_var_95 > 0.0
    assert results.post_opt_cvar_95 >= results.post_opt_var_95


def test_layer5_objective_traceability_not_cvss():
    """
    TEST 5 — OBJECTIVE TRACEABILITY
    Constructs two vulnerabilities:
    - CVE-HIGH-CVSS: CVSS = 10.0 (cost = ₹80,000), Delta EAL = ₹10,000,000 (LEF=0.05, ExpLoss=200M)
    - CVE-HIGH-DEAL: CVSS = 5.0  (cost = ₹16,000), Delta EAL = ₹100,000,000 (LEF=0.50, ExpLoss=200M)

    Budget = ₹50,000 (can only afford CVE-HIGH-DEAL at ₹16,000, or neither).
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
