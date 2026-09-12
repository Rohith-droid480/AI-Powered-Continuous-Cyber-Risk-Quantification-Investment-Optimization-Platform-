from fastapi import FastAPI, UploadFile, File, HTTPException, status
from typing import Dict, Any

from app.schemas import (
    JobStatus,
    JobStatusEnum,
    SimulationResults,
    OptimizationResults,
    PerCveRiskSummary,
)

app = FastAPI(
    title="Continuous Cyber Risk Quantification & Investment Optimization API",
    version="0.1.0",
    description="Backend API stubs for scan upload, risk simulation, and patch optimization.",
)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Cyber Risk Quantification API is active."}


@app.post("/scan/upload", response_model=JobStatus, status_code=status.HTTP_200_OK)
async def upload_scan(file: UploadFile = File(None)):
    """
    POST /scan/upload - Accepts Nessus XML scan file upload and returns job_id instantly.
    """
    return JobStatus(
        job_id="job_stub_001",
        status=JobStatusEnum.PARSED,
        message="Scan file received and initial parsing completed (stub)."
    )


@app.get("/scan/{job_id}/results", status_code=status.HTTP_200_OK)
async def get_scan_results(job_id: str) -> Dict[str, Any]:
    """
    GET /scan/{job_id}/results - Returns stub risk quantification and optimization results.
    """
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
        ]
    )

    stub_opt_results = OptimizationResults(
        job_id=job_id,
        budget=50000.0,
        selected_cves=["CVE-2021-44228"],
        total_cost=1600.0,
        post_opt_eal=75000.0,
        post_opt_var_95=175000.0,
        post_opt_cvar_95=210000.0,
        delta_eal_per_cve={"CVE-2021-44228": 75000.0}
    )

    return {
        "job_id": job_id,
        "status": JobStatusEnum.COMPLETED.value,
        "simulation_results": stub_sim_results.model_dump(),
        "optimization_results": stub_opt_results.model_dump(),
    }
