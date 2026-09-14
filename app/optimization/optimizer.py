"""
Layer 5 - Patch Investment Optimization Engine

This module implements 0/1 Knapsack optimization using PuLP to select remediations
that maximize Expected Annual Loss reduction (Delta EAL) under a finite budget constraint.

Methodological Notes:
- Objective: Maximize sum(Delta EAL_k * x_k) where Delta EAL_k = LEF_k * E[Loss Magnitude_k].
- Decision Variable: x_k in {0, 1} for each unique CVE.
- Constraint: sum(Cost_k * x_k) <= Budget.
- Patch Effort: CVSS >= 9.0 (40h), 7.0 <= CVSS < 9.0 (16h), 4.0 <= CVSS < 7.0 (8h), CVSS < 4.0 (4h).
- Monetary Cost: Effort (hours) * hourly_rate in Indian Rupees (INR / ₹). Default ₹2,000/hour.
- Post-optimization re-simulation: Filters selected CVEs out and runs Layer 4 Monte Carlo once.
"""

import logging
import math
from typing import List, Dict, Tuple, Optional
import pulp
import numpy as np

from app.schemas.models import (
    CalibratedRiskRecord,
    OptimizationResults,
    JobStatus,
    JobStatusEnum,
)
from app.simulation.engine import run_monte_carlo_simulation

logger = logging.getLogger(__name__)


def calculate_patch_cost(cvss_score: float, hourly_rate: float = 2000.0) -> float:
    """
    Calculate the remediation patch cost for a vulnerability based on CVSS score and hourly labor rate.

    Effort mapping:
    - Critical (CVSS >= 9.0): 40 hours
    - High (7.0 <= CVSS < 9.0): 16 hours
    - Medium (4.0 <= CVSS < 7.0): 8 hours
    - Low (CVSS < 4.0): 4 hours

    Cost (in INR / ₹):
        Cost_k = EffortHours_k * hourly_rate

    :param cvss_score: CVSS base score in range [0.0, 10.0].
    :param hourly_rate: Labor cost per hour in INR (₹). Default is ₹2,000/hour.
    :return: Total patch cost in INR (₹).
    """
    cvss = float(cvss_score)
    rate = float(hourly_rate)

    if cvss >= 9.0:
        effort_hours = 40.0
    elif cvss >= 7.0:
        effort_hours = 16.0
    elif cvss >= 4.0:
        effort_hours = 8.0
    else:
        effort_hours = 4.0

    return effort_hours * rate
