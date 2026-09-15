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


def optimize_patch_investments(
    risk_records: List[CalibratedRiskRecord],
    budget: float,
    hourly_rate: float = 2000.0,
    job_id: str = "job_opt_001",
    num_iterations: int = 100_000,
    seed: Optional[int] = None,
) -> Tuple[Optional[OptimizationResults], Optional[JobStatus]]:
    """
    Solves the 0/1 Knapsack Patch Investment Optimization using PuLP and performs
    stochastic post-optimization Monte Carlo re-simulation.

    :param risk_records: List of Layer 3 CalibratedRiskRecord objects.
    :param budget: Remediation budget constraint in INR (₹).
    :param hourly_rate: Labor cost per hour in INR (₹). Default is ₹2,000/hour.
    :param job_id: Identifier string for the job.
    :param num_iterations: Number of Monte Carlo iterations for re-simulation. Default 100,000.
    :param seed: Optional integer seed for reproducible re-simulation.
    :return: Tuple of (OptimizationResults, None) on success, or (None, JobStatus) on failure.
    """
    # 1. Edge Case: Negative budget
    if budget < 0:
        return None, JobStatus(
            job_id=job_id,
            status=JobStatusEnum.OPTIMIZATION_UNAVAILABLE,
            message=f"Remediation budget cannot be negative, got {budget}.",
        )

    # 2. Edge Case: Invalid hourly rate or non-finite inputs
    if hourly_rate <= 0 or not np.isfinite(hourly_rate) or not np.isfinite(budget):
        return None, JobStatus(
            job_id=job_id,
            status=JobStatusEnum.OPTIMIZATION_UNAVAILABLE,
            message="Invalid or non-finite numerical parameters for budget or hourly rate.",
        )

    # 3. Edge Case: Empty risk_records
    if not risk_records or len(risk_records) == 0:
        return None, JobStatus(
            job_id=job_id,
            status=JobStatusEnum.OPTIMIZATION_UNAVAILABLE,
            message="Input risk records list is empty.",
        )

    # 4. Extract per-CVE Delta EAL and patch costs
    cve_data: Dict[str, Dict[str, float]] = {}

    for idx, rec in enumerate(risk_records):
        cve_id = rec.vulnerability.cve_id
        lef = float(rec.lef)
        exp_loss = float(rec.expected_loss_magnitude)
        cvss = float(rec.vulnerability.cvss_score)

        if lef < 0 or not np.isfinite(lef) or not np.isfinite(exp_loss) or exp_loss < 0 or not np.isfinite(cvss):
            return None, JobStatus(
                job_id=job_id,
                status=JobStatusEnum.OPTIMIZATION_UNAVAILABLE,
                message=f"Invalid record numerical parameters at index {idx} for CVE {cve_id}.",
            )

        # Delta EAL_k = LEF_k * E[Loss Magnitude_k]
        rec_delta_eal = lef * exp_loss

        if cve_id not in cve_data:
            cve_data[cve_id] = {
                "delta_eal": rec_delta_eal,
                "max_cvss": cvss,
            }
        else:
            cve_data[cve_id]["delta_eal"] += rec_delta_eal
            cve_data[cve_id]["max_cvss"] = max(cve_data[cve_id]["max_cvss"], cvss)

    cve_ids = list(cve_data.keys())

    # Calculate patch cost per unique CVE
    for cve in cve_ids:
        cost = calculate_patch_cost(cve_data[cve]["max_cvss"], hourly_rate)
        cve_data[cve]["cost"] = cost

    # 5. PuLP 0/1 Knapsack Optimization
    try:
        prob = pulp.LpProblem("Patch_Investment_Optimization", pulp.LpMaximize)

        # Binary decision variables x_c in {0, 1}
        x_vars = {cve: prob.add_variable(f"x_{i}", lowBound=0, upBound=1, cat=pulp.LpBinary) for i, cve in enumerate(cve_ids)}

        # Objective: Maximize total Delta EAL
        prob += pulp.lpSum([cve_data[cve]["delta_eal"] * x_vars[cve] for cve in cve_ids]), "Total_Delta_EAL"

        # Constraint: Total patch cost <= Budget
        prob += pulp.lpSum([cve_data[cve]["cost"] * x_vars[cve] for cve in cve_ids]) <= budget, "Budget_Constraint"

        solver = pulp.PULP_CBC_CMD(msg=False)
        prob.solve(solver)

        if prob.status != pulp.LpStatusOptimal:
            return None, JobStatus(
                job_id=job_id,
                status=JobStatusEnum.OPTIMIZATION_UNAVAILABLE,
                message=f"PuLP solver failed to find optimal solution: status {pulp.LpStatus[prob.status]}.",
            )
    except Exception as e:
        logger.error("PuLP solver exception for job %s: %s", job_id, str(e), exc_info=True)
        return None, JobStatus(
            job_id=job_id,
            status=JobStatusEnum.OPTIMIZATION_UNAVAILABLE,
            message=f"PuLP solver exception: {str(e)}",
        )

    # 6. Extract selected CVEs & totals
    selected_cves: List[str] = []
    total_cost = 0.0
    delta_eal_per_cve: Dict[str, float] = {}

    for cve in cve_ids:
        val = pulp.value(x_vars[cve])
        if val is not None and val > 0.5:
            selected_cves.append(cve)
            total_cost += cve_data[cve]["cost"]
            delta_eal_per_cve[cve] = cve_data[cve]["delta_eal"]

    # Sort selected CVEs for deterministic output ordering
    selected_cves.sort()

    # 7. Post-Optimization Re-Simulation
    remaining_records = [rec for rec in risk_records if rec.vulnerability.cve_id not in selected_cves]

    if len(remaining_records) == 0:
        # Deliberate business rule: an empty remaining set after optimization is a legitimate business outcome
        # ("100% of scanned vulnerabilities have been remediated under budget"), NOT a simulation failure.
        # We explicitly set post_opt_eal=0, post_opt_var_95=0, post_opt_cvar_95=0 without calling Layer 4 engine.
        post_opt_eal = 0.0
        post_opt_var_95 = 0.0
        post_opt_cvar_95 = 0.0
    else:

        sim_results, sim_job = run_monte_carlo_simulation(
            risk_records=remaining_records,
            num_iterations=num_iterations,
            job_id=f"{job_id}_post_opt",
            seed=seed,
        )

        if sim_job is not None or sim_results is None:
            msg = sim_job.message if sim_job else "Unknown simulation error"
            return None, JobStatus(
                job_id=job_id,
                status=JobStatusEnum.OPTIMIZATION_UNAVAILABLE,
                message=f"Post-optimization simulation failed: {msg}",
            )

        post_opt_eal = sim_results.eal
        post_opt_var_95 = sim_results.var_95
        post_opt_cvar_95 = sim_results.cvar_95

    return OptimizationResults(
        job_id=job_id,
        budget=float(budget),
        selected_cves=selected_cves,
        total_cost=float(total_cost),
        post_opt_eal=float(post_opt_eal),
        post_opt_var_95=float(post_opt_var_95),
        post_opt_cvar_95=float(post_opt_cvar_95),
        delta_eal_per_cve=delta_eal_per_cve,
    ), None
