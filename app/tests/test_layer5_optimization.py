import pytest
from app.optimization.optimizer import calculate_patch_cost


def test_layer5_patch_cost_calculation_tiers():
    """
    Test 1: Cost Tiers Calculation
    Verifies exact remediation costs for Critical, High, Medium, and Low CVSS tiers
    with hourly_rate = ₹2,000/hr.
    - Critical (CVSS >= 9.0): 40 hrs * 2000 = ₹80,000
    - High (7.0 <= CVSS < 9.0): 16 hrs * 2000 = ₹32,000
    - Medium (4.0 <= CVSS < 7.0): 8 hrs * 2000 = ₹16,000
    - Low (CVSS < 4.0): 4 hrs * 2000 = ₹8,000
    """
    rate = 2000.0

    # Critical tier (e.g. CVSS 10.0, 9.5, 9.0)
    assert calculate_patch_cost(10.0, rate) == 80000.0
    assert calculate_patch_cost(9.5, rate) == 80000.0
    assert calculate_patch_cost(9.0, rate) == 80000.0

    # High tier (e.g. CVSS 8.9, 7.5, 7.0)
    assert calculate_patch_cost(8.9, rate) == 32000.0
    assert calculate_patch_cost(7.5, rate) == 32000.0
    assert calculate_patch_cost(7.0, rate) == 32000.0

    # Medium tier (e.g. CVSS 6.9, 5.0, 4.0)
    assert calculate_patch_cost(6.9, rate) == 16000.0
    assert calculate_patch_cost(5.0, rate) == 16000.0
    assert calculate_patch_cost(4.0, rate) == 16000.0

    # Low tier (e.g. CVSS 3.9, 2.6, 0.0)
    assert calculate_patch_cost(3.9, rate) == 8000.0
    assert calculate_patch_cost(2.6, rate) == 8000.0
    assert calculate_patch_cost(0.0, rate) == 8000.0
