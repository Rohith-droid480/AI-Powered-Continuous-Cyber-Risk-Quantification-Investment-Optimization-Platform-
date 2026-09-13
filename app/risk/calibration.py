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
    
    We anchor the mean of our assumed LogNormal primary-loss distribution to IBM's
    reported 2026 India average total breach cost (₹255,000,000). The dispersion (CV=2.0)
    and the resulting μ≈18.5520, σ≈1.2686 are our own assumption and mathematical transformation
    — IBM does not publish a LogNormal mean or these distribution parameters directly.
    
    :param mean_loss: Mean breach loss in INR (₹). Default ₹255,000,000.
    :param cv_loss: Coefficient of variation (dimensionless). Default 2.0.
    :return: Tuple of (mu, sigma, expected_primary_loss) in INR (₹).
    """
    # Primary Loss: We anchor the mean of our assumed LogNormal primary-loss distribution to IBM's
    # reported 2026 India average total breach cost (₹255,000,000). The dispersion (CV=2.0) and the
    # resulting μ≈18.5520, σ≈1.2686 are our own assumption and mathematical transformation — IBM does
    # not publish a LogNormal mean or these distribution parameters directly.
    mu_x = float(mean_loss)
    cv_x = float(cv_loss)
    
    sigma_sq = math.log(1.0 + cv_x ** 2)
    sigma = math.sqrt(sigma_sq)
    mu = math.log(mu_x) - 0.5 * sigma_sq
    expected_primary_loss = mu_x
    
    return mu, sigma, expected_primary_loss


def calculate_secondary_loss(
    primary_loss: float,
    secondary_ratio: float = 0.4
) -> float:
    """
    Calculate Secondary Loss based on Primary Loss.
    
    Secondary Loss = 0.4 × Primary Loss. This 0.4 multiplier is our own conservative
    illustrative assumption, accounting for additional non-primary costs (regulatory,
    reputational, customer churn) not fully captured in the primary-loss anchor. It is
    not derived from an IBM cost-category percentage, and is not specific to DPDPA —
    DPDPA is only an example of the kind of exposure this margin is meant to cover, not its source.
    
    :param primary_loss: Expected Primary Loss in INR (₹).
    :param secondary_ratio: Multiplier for secondary loss exposure. Default is 0.4.
    :return: Expected Secondary Loss in INR (₹).
    """
    # Secondary Loss = 0.4 × Primary Loss. This 0.4 multiplier is our own conservative illustrative
    # assumption, accounting for additional non-primary costs (regulatory, reputational, customer churn)
    # not fully captured in the primary-loss anchor. It is not derived from an IBM cost-category percentage,
    # and is not specific to DPDPA — DPDPA is only an example of the kind of exposure this margin is meant to cover, not its source.
    return float(primary_loss) * float(secondary_ratio)



def calculate_loss_magnitude(primary_loss: float, secondary_loss: float) -> float:
    """
    Calculate total Loss Magnitude.
    
    Formula: Loss Magnitude = Primary Loss + Secondary Loss
    
    :param primary_loss: Expected Primary Loss in INR (₹).
    :param secondary_loss: Expected Secondary Loss in INR (₹).
    :return: Total Loss Magnitude in INR (₹).
    """
    return float(primary_loss) + float(secondary_loss)


def calibrate_vulnerability_risk(
    vulnerability: EnrichedVulnerability,
    rs: float = 0.5,
    base_contact_rate: float = 2.0,
    exposure_factor: float = 0.5,
    mean_primary_loss: float = 255_000_000.0,
    cv_primary_loss: float = 2.0
) -> CalibratedRiskRecord:
    """
    Pipeline function to compute full Layer 3 risk calibration for a given vulnerability.
    
    Returns an instance of CalibratedRiskRecord matching app/schemas/models.py.
    """
    # 1. TCap
    t_cap = calculate_tcap(is_kev=vulnerability.is_kev, epss_score=vulnerability.epss_score)
    
    # 2. RS validation
    validated_rs = calculate_rs(rs)
    
    # 3. Vuln
    vuln = calculate_vuln(t_cap=t_cap, rs=validated_rs)
    
    # 4. TEF
    tef = calculate_tef(base_contact_rate=base_contact_rate, exposure_factor=exposure_factor)
    
    # 5. LEF
    lef = calculate_lef(tef=tef, vuln=vuln)
    
    # 6. Primary Loss calibration
    mu, sigma, exp_primary = calibrate_primary_loss(mean_loss=mean_primary_loss, cv_loss=cv_primary_loss)
    
    # 7. Secondary Loss
    exp_secondary = calculate_secondary_loss(primary_loss=exp_primary, secondary_ratio=0.4)
    
    # 8. Loss Magnitude
    loss_magnitude = calculate_loss_magnitude(primary_loss=exp_primary, secondary_loss=exp_secondary)
    
    return CalibratedRiskRecord(
        vulnerability=vulnerability,
        t_cap=t_cap,
        rs=validated_rs,
        vuln=vuln,
        tef=tef,
        lef=lef,
        primary_loss_mu=mu,
        primary_loss_sigma=sigma,
        expected_primary_loss=exp_primary,
        expected_secondary_loss=exp_secondary,
        expected_loss_magnitude=loss_magnitude
    )








