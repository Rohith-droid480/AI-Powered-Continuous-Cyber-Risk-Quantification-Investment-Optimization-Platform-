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
