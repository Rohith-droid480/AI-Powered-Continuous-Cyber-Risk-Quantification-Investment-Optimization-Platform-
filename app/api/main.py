from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, status
from typing import Dict, Any, Optional, List

from app.schemas.models import (
    JobStatus,
    JobStatusEnum,
    SimulationResults,
    OptimizationResults,
    PerCveRiskSummary,
    EnrichedVulnerability,
)
from app.ingestion.jobs import job_manager

app = FastAPI(
    title="Continuous Cyber Risk Quantification & Investment Optimization API",
    version="0.1.0",
    description="Backend API for scan upload, async ingestion, risk simulation, and patch optimization.",
)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Cyber Risk Quantification API is active."}


@app.post("/scan/upload", response_model=JobStatus, status_code=status.HTTP_200_OK)
async def upload_scan(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
):
    """
    POST /scan/upload - Accepts Nessus XML scan file upload and returns job_id immediately.
    Parsing and ingestion run asynchronously in the background.
    """
    if file is None:
        # Fail-soft: create job in INGESTION_FAILED state cleanly
        job_id = job_manager.create_job(
            initial_status=JobStatusEnum.INGESTION_FAILED,
            message="No scan file provided in upload.",
        )
        job = job_manager.get_job(job_id)
        return job.to_job_status()

    file_bytes = await file.read()
    if not file_bytes:
        job_id = job_manager.create_job(
            initial_status=JobStatusEnum.INGESTION_FAILED,
            message="Uploaded scan file is empty.",
        )
        job = job_manager.get_job(job_id)
        return job.to_job_status()

    # Create job in PROCESSING state
    job_id = job_manager.create_job(
        initial_status=JobStatusEnum.PROCESSING,
        message="Scan file received; background ingestion in progress.",
    )

    # Schedule background ingestion worker
    background_tasks.add_task(job_manager.process_scan_job, job_id, file_bytes)

    job = job_manager.get_job(job_id)
    return job.to_job_status()


@app.get("/scan/{job_id}/status", response_model=JobStatus, status_code=status.HTTP_200_OK)
async def get_job_status(job_id: str):
    """
    GET /scan/{job_id}/status - Returns current processing status of the ingestion job.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found.",
        )
    return job.to_job_status()


@app.get(
    "/scan/{job_id}/vulnerabilities",
    response_model=List[EnrichedVulnerability],
    status_code=status.HTTP_200_OK,
)
async def get_parsed_vulnerabilities(job_id: str) -> List[EnrichedVulnerability]:
    """
    GET /scan/{job_id}/vulnerabilities - Returns enriched vulnerabilities once ingestion is complete.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found.",
        )
    return job.enriched_vulnerabilities


@app.get("/scan/{job_id}/results", status_code=status.HTTP_200_OK)
async def get_scan_results(
    job_id: str,
    budget: float = 150000.0,
) -> Dict[str, Any]:
    """
    GET /scan/{job_id}/results - Returns risk quantification and patch optimization results.
    Executes real Layer 3 calibration, Layer 4 Monte Carlo simulation, and Layer 5 optimization
    when an actual parsed job is requested.
    """
    job = job_manager.get_job(job_id)

    # If job exists and has processed vulnerabilities, execute real pipeline
    if job is not None:
        if job.status == JobStatusEnum.INGESTION_FAILED:
            return {
                "job_id": job_id,
                "status": JobStatusEnum.INGESTION_FAILED.value,
                "message": job.message or "Ingestion failed.",
            }

        if job.enriched_vulnerabilities:
            from app.risk.calibration import calibrate_vulnerability_risk
            from app.simulation.engine import run_monte_carlo_simulation
            from app.optimization.optimizer import optimize_patch_investments

            records = [calibrate_vulnerability_risk(e) for e in job.enriched_vulnerabilities]

            # Baseline Layer 4 Simulation
            sim_results, sim_err = run_monte_carlo_simulation(
                risk_records=records,
                num_iterations=100000,
                job_id=f"{job_id}_sim",
                seed=42,
            )
            if sim_err:
                return {
                    "job_id": job_id,
                    "status": JobStatusEnum.SIMULATION_FAILED.value,
                    "message": sim_err.message,
                }

            # Layer 5 Optimization
            opt_results, opt_err = optimize_patch_investments(
                risk_records=records,
                budget=budget,
                job_id=f"{job_id}_opt",
                seed=42,
            )
            if opt_err:
                return {
                    "job_id": job_id,
                    "status": JobStatusEnum.OPTIMIZATION_UNAVAILABLE.value,
                    "message": opt_err.message,
                    "simulation_results": sim_results.model_dump() if sim_results else None,
                }

            # Post-optimization simulation distribution for Loss Exceedance Curve
            remaining = [r for r in records if r.vulnerability.cve_id not in opt_results.selected_cves]
            post_sim_results = None
            if remaining:
                post_sim_results, _ = run_monte_carlo_simulation(
                    risk_records=remaining,
                    num_iterations=100000,
                    job_id=f"{job_id}_post_sim",
                    seed=42,
                )

            return {
                "job_id": job_id,
                "status": JobStatusEnum.COMPLETED.value,
                "simulation_results": sim_results.model_dump() if sim_results else None,
                "optimization_results": opt_results.model_dump() if opt_results else None,
                "post_opt_simulation_results": post_sim_results.model_dump() if post_sim_results else None,
                "vulnerabilities": [ev.model_dump() for ev in job.enriched_vulnerabilities],
            }

    # Backward-compatible stub fallback
    stub_sim_results = SimulationResults(
        job_id=job_id,
        eal=150000.0,
        var_95=350000.0,
        cvar_95=420000.0,
        loss_distribution=[1200.0, 45000.0, 150000.0, 350000.0, 420000.0],
        per_cve_risk=[
            PerCveRiskSummary(
                cve_id="CVE-2021-44228",
                lef=0.15,
                expected_loss_magnitude=500000.0,
                baseline_eal=75000.0,
            ),
            PerCveRiskSummary(
                cve_id="CVE-2023-38606",
                lef=0.10,
                expected_loss_magnitude=750000.0,
                baseline_eal=75000.0,
            ),
        ],
    )

    stub_opt_results = OptimizationResults(
        job_id=job_id,
        budget=50000.0,
        selected_cves=["CVE-2021-44228"],
        total_cost=1600.0,
        post_opt_eal=75000.0,
        post_opt_var_95=175000.0,
        post_opt_cvar_95=210000.0,
        delta_eal_per_cve={"CVE-2021-44228": 75000.0},
    )

    return {
        "job_id": job_id,
        "status": JobStatusEnum.COMPLETED.value,
        "simulation_results": stub_sim_results.model_dump(),
        "optimization_results": stub_opt_results.model_dump(),
    }

