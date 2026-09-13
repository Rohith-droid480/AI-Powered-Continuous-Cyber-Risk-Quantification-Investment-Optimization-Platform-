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


def calculate_tef(base_contact_rate: float, exposure_factor: float) -> float:
    """
    Calculate Threat Event Frequency (TEF).
    
    Formula: TEF = base contact rate * asset internet-exposure factor
    
    :param base_contact_rate: Base annual contact rate in events/year.
    :param exposure_factor: Internet exposure factor multiplier (0.0 to 1.0+).
    :return: TEF float value in events/year.
    """
    return float(base_contact_rate) * float(exposure_factor)


def calculate_lef(tef: float, vuln: float) -> float:
    """
    Calculate Loss Event Frequency (LEF).
    
    Formula: LEF = TEF * Vuln
    
    :param tef: Threat Event Frequency in events/year.
    :param vuln: Vulnerability ratio in range [0.0, 1.0].
    :return: LEF float value in loss events/year.
    """
    # FAIR-STRUCTURAL: LEF = TEF * Vuln.
    # This relationship is the FAIR-structural portion of Layer 3.
    # The upstream TCap/RS calibration is our modeling assumption and is not
    # being represented as canonical FAIR.
    return float(tef) * float(vuln)


def calibrate_primary_loss(
    mean_loss: float = 255_000_000.0,
    cv_loss: float = 2.0
) -> Tuple[float, float, float]:
    """
    Calibrate LogNormal parameters (mu, sigma) for Primary Loss.
    
    Primary Loss ~ LogNormal(mu, sigma)
    
    Calibration Inputs:
    - mean_loss (mu_X): ₹255,000,000 (IBM India 2026 all-sector mean breach cost in INR).
    - cv_loss (CV_X): 2.0 (coefficient of variation assumption within empirical 1.5-2.5 range).
    
    Equations:
    - sigma^2 = ln(1 + CV_X^2) = ln(1 + 4) = ln(5) => sigma = sqrt(ln(5)) approx 1.2686
    - mu = ln(mu_X) - 0.5 * sigma^2 = ln(255,000,000) - 0.5 * ln(5) approx 18.5520
    - E[Primary Loss] = exp(mu + 0.5 * sigma^2) = mu_X = ₹255,000,000
    
    :param mean_loss: Mean breach loss in INR (₹).
    :param cv_loss: Coefficient of variation (dimensionless).
    :return: Tuple of (mu, sigma, expected_primary_loss) in INR (₹).
    """
    # CV_X = 2.0 is our modeling assumption, while mu_X = ₹255,000,000 is the directly sourced IBM India value.
    mu_x = float(mean_loss)
    cv_x = float(cv_loss)
    
    sigma_sq = math.log(1.0 + cv_x ** 2)
    sigma = math.sqrt(sigma_sq)
    mu = math.log(mu_x) - 0.5 * sigma_sq
    expected_primary_loss = mu_x
    
    return mu, sigma, expected_primary_loss





