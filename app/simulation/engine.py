"""
Layer 4 - Monte Carlo Engine

Synchronous, fast, vectorized Monte Carlo engine for Cyber Risk Quantification.

Vectorization Requirement:
- No Python for-loop iterates over the 100,000 simulation trials.
- Uses numpy.random.default_rng() exclusively (legacy random generator is prohibited).
- Per-vulnerability LogNormal parameters (mu, sigma) are preserved per sampled event.
- Secondary loss ratio (0.4) is applied per event draw (Loss_i = 1.4 * Primary_i).

"""

from typing import List, Tuple, Optional
import numpy as np
from app.schemas.models import (
    CalibratedRiskRecord,
    PerCveRiskSummary,
    SimulationResults,
    JobStatus,
    JobStatusEnum,
)


def run_monte_carlo_simulation(
    risk_records: List[CalibratedRiskRecord],
    num_iterations: int = 100_000,
    job_id: str = "job_sim_001",
    seed: Optional[int] = None,
) -> Tuple[Optional[SimulationResults], Optional[JobStatus]]:
    """
    Run vectorized Monte Carlo simulation over input CalibratedRiskRecords.
    
    :param risk_records: List of Layer 3 CalibratedRiskRecord objects.
    :param num_iterations: Number of simulation trials (default 100,000).
    :param job_id: Identifier string for the simulation job.
    :param seed: Optional integer seed for reproducibility (uses default_rng(seed)).
    :return: Tuple of (SimulationResults, None) on success, or (None, JobStatus) on failure.
    """
    # 1. Input Validation for SIMULATION_FAILED state
    if not risk_records or len(risk_records) == 0:
        return None, JobStatus(
            job_id=job_id,
            status=JobStatusEnum.SIMULATION_FAILED,
            message="Input vulnerability list is empty.",
        )
    
    for idx, rec in enumerate(risk_records):
        if rec.lef < 0 or not np.isfinite(rec.primary_loss_mu) or rec.primary_loss_sigma <= 0 or not np.isfinite(rec.primary_loss_sigma):
            return None, JobStatus(
                job_id=job_id,
                status=JobStatusEnum.SIMULATION_FAILED,
                message=f"Invalid record parameters at index {idx}: LEF={rec.lef}, mu={rec.primary_loss_mu}, sigma={rec.primary_loss_sigma}",
            )
    
    # 2. Extract per-CVE risk summaries and arrays
    cve_ids = []
    lefs = []
    mus = []
    sigmas = []
    per_cve_summaries = []
    
    for rec in risk_records:
        cve_id = rec.vulnerability.cve_id
        lef = float(rec.lef)
        exp_loss = float(rec.expected_loss_magnitude)
        baseline_eal = lef * exp_loss
        
        cve_ids.append(cve_id)
        lefs.append(lef)
        mus.append(float(rec.primary_loss_mu))
        sigmas.append(float(rec.primary_loss_sigma))
        
        per_cve_summaries.append(
            PerCveRiskSummary(
                cve_id=cve_id,
                lef=lef,
                expected_loss_magnitude=exp_loss,
                baseline_eal=baseline_eal,
            )
        )
    
    total_lef = sum(lefs)
    if total_lef <= 0:
        # Zero risk events
        return SimulationResults(
            job_id=job_id,
            eal=0.0,
            var_95=0.0,
            cvar_95=0.0,
            loss_distribution=[0.0] * num_iterations,
            per_cve_risk=per_cve_summaries,
        ), None
    
    # VECTORIZATION REQUIREMENT:
    # Use numpy.random.default_rng() exclusively.
    # No Python for-loop iterates over the 100,000 simulation trials.
    rng = np.random.default_rng(seed)
    
    # Draw Poisson event counts N_j for all num_iterations in one vectorized call
    event_counts = rng.poisson(lam=total_lef, size=num_iterations)
    total_events = int(np.sum(event_counts))
    
    if total_events == 0:
        annual_losses = np.zeros(num_iterations, dtype=np.float64)
    else:
        # Sample relative vulnerability assignments for all total_events
        probs = np.array(lefs, dtype=np.float64) / total_lef
        num_vulns = len(risk_records)
        
        if num_vulns == 1:
            sampled_vuln_indices = np.zeros(total_events, dtype=np.int64)
        else:
            sampled_vuln_indices = rng.choice(num_vulns, size=total_events, p=probs)
        
        # Gather per-event LogNormal parameters
        sampled_mus = np.array(mus, dtype=np.float64)[sampled_vuln_indices]
        sampled_sigmas = np.array(sigmas, dtype=np.float64)[sampled_vuln_indices]
        
        # Draw LogNormal primary losses for all total_events in one call
        primary_losses = rng.lognormal(mean=sampled_mus, sigma=sampled_sigmas)
        
        # Loss_i = Primary_i + Secondary_i = 1.4 * Primary_i
        event_losses = primary_losses * 1.4
        
        # Map each event to its iteration index using np.repeat and aggregate with np.bincount
        iteration_indices = np.repeat(np.arange(num_iterations, dtype=np.int64), event_counts)
        annual_losses = np.bincount(iteration_indices, weights=event_losses, minlength=num_iterations)
    
    # 3. Compute summary metrics from 100,000 trial annual losses
    eal = float(np.mean(annual_losses))
    var_95 = float(np.percentile(annual_losses, 95))
    tail_losses = annual_losses[annual_losses >= var_95]
    cvar_95 = float(np.mean(tail_losses)) if len(tail_losses) > 0 else var_95
    
    return SimulationResults(
        job_id=job_id,
        eal=eal,
        var_95=var_95,
        cvar_95=cvar_95,
        loss_distribution=annual_losses.tolist(),
        per_cve_risk=per_cve_summaries,
    ), None
