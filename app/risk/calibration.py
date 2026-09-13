"""
Layer 3 - Risk Calibration Engine

This module implements FAIR-aligned loss event frequency (LEF) and loss magnitude
calibration.

Methodological Notes:
- TCap / RS mapping and the resulting vulnerability ratio formula are OUR MODELING ASSUMPTIONS,
  not canonical FAIR definitions.
- LEF = TEF * Vuln is FAIR-STRUCTURAL (canonical FAIR relationship).
- All monetary loss values are in Indian Rupees (₹ / INR).
"""

from typing import Tuple, Optional
import math
from app.schemas.models import EnrichedVulnerability, CalibratedRiskRecord


def calculate_tcap(is_kev: bool, epss_score: float) -> float:
    """
    Calculate Threat Capability (TCap).
    
    Rule:
    - KEV = true  -> TCap = 1.0 (exploit maturity is confirmed active)
    - KEV = false -> TCap = EPSS score
    
    Note: TCap / RS mapping and calibration are OUR MODELING ASSUMPTIONS,
    not canonical FAIR definitions.
    
    :param is_kev: Flag indicating if vulnerability is in CISA KEV catalog.
    :param epss_score: EPSS probability score in range [0.0, 1.0].
    :return: TCap float value in range [0.0, 1.0].
    """
    # TCap / RS mapping is OUR MODELING ASSUMPTION, not canonical FAIR.
    if is_kev:
        return 1.0
    return float(epss_score)


def calculate_rs(rs: float = 0.5) -> float:
    """
    Validate and return organizational baseline Resistance Strength (RS).
    
    RS represents the defensive capability of the target asset/organization
    constrained strictly to the range [0.0, 1.0].
    
    Note: TCap / RS mapping and calibration are OUR MODELING ASSUMPTIONS,
    not canonical FAIR definitions.
    
    :param rs: Defense score float in range [0.0, 1.0]. Default is 0.5.
    :return: Validated RS float score.
    :raises ValueError: If RS is outside [0.0, 1.0].
    """
    # TCap / RS mapping is OUR MODELING ASSUMPTION, not canonical FAIR.
    rs_val = float(rs)
    if not (0.0 <= rs_val <= 1.0):
        raise ValueError(f"RS score must be between 0.0 and 1.0 inclusive, got {rs_val}")
    return rs_val


def calculate_vuln(t_cap: float, rs: float) -> float:
    """
    Calculate Vulnerability ratio (Vuln).
    
    Formula: Vuln = TCap / (TCap + RS)
    
    Note: TCap / RS mapping and calibration are OUR MODELING ASSUMPTIONS,
    not canonical FAIR definitions.
    
    :param t_cap: Threat Capability float in range [0.0, 1.0].
    :param rs: Resistance Strength float in range [0.0, 1.0].
    :return: Vulnerability ratio float in range [0.0, 1.0].
    :raises ValueError: If (t_cap + rs) <= 0.
    """
    # TCap / RS mapping is OUR MODELING ASSUMPTION, not canonical FAIR.
    denominator = float(t_cap) + float(rs)
    if denominator <= 0:
        raise ValueError(f"Denominator (TCap + RS) must be greater than 0, got {denominator}")
    return float(t_cap) / denominator


