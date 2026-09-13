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
