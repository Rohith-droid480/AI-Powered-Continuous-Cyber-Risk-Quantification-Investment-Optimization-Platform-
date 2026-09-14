from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class JobStatusEnum(str, Enum):
    PARSED = "PARSED"
    INGESTION_FAILED = "INGESTION_FAILED"
    SIMULATION_FAILED = "SIMULATION_FAILED"
    OPTIMIZATION_UNAVAILABLE = "OPTIMIZATION_UNAVAILABLE"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"


class JobStatus(BaseModel):
    job_id: str
    status: JobStatusEnum
    message: Optional[str] = None


class ParsedVulnerability(BaseModel):
    cve_id: str = Field(..., description="CVE identifier, e.g. CVE-2021-44228")
    plugin_id: str = Field(..., description="Nessus plugin ID")
    plugin_name: str = Field(..., description="Nessus plugin name")
    host: str = Field(..., description="Target host IP or hostname")
    port: int = Field(0, description="Port number")
    protocol: str = Field("tcp", description="Network protocol")
    severity: int = Field(0, description="Nessus raw severity (0-4)")
    description: Optional[str] = Field(None, description="Vulnerability description")


class EnrichmentStatus(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"


class EnrichedVulnerability(ParsedVulnerability):
    cvss_score: float = Field(0.0, ge=0.0, le=10.0, description="CVSS base score")
    epss_score: float = Field(0.001, ge=0.0, le=1.0, description="EPSS score")
    is_kev: bool = Field(False, description="Known Exploited Vulnerability flag")
    enrichment_status: EnrichmentStatus = Field(EnrichmentStatus.PARTIAL, description="Enrichment status: FULL or PARTIAL")


class CalibratedRiskRecord(BaseModel):
    vulnerability: EnrichedVulnerability
    t_cap: float = Field(..., description="Threat Capability (KEV=1.0 else EPSS)")
    rs: float = Field(..., description="Resistance Strength / defense score (0-1)")
    vuln: float = Field(..., description="Vulnerability ratio TCap / (TCap + RS)")
    tef: float = Field(..., description="Threat Event Frequency")
    lef: float = Field(..., description="Loss Event Frequency (TEF * Vuln)")
    primary_loss_mu: float = Field(..., description="LogNormal mu parameter for Primary Loss")
    primary_loss_sigma: float = Field(..., description="LogNormal sigma parameter for Primary Loss")
    expected_primary_loss: float = Field(..., description="Expected Primary Loss")
    expected_secondary_loss: float = Field(..., description="Expected Secondary Loss (0.4 * Primary Loss)")
    expected_loss_magnitude: float = Field(..., description="Expected Loss Magnitude (Primary + Secondary)")


class PerCveRiskSummary(BaseModel):
    cve_id: str
    lef: float
    expected_loss_magnitude: float
    baseline_eal: float


class LecPoint(BaseModel):
    loss: float = Field(..., description="Annual loss magnitude in INR (₹)")
    exceedance_probability: float = Field(..., description="Empirical exceedance probability in percentage (0-100%)")


class SimulationResults(BaseModel):
    job_id: str
    eal: float = Field(..., description="Expected Annual Loss")
    var_95: float = Field(..., description="Value at Risk at 95th percentile")
    cvar_95: float = Field(..., description="Conditional Value at Risk at 95th percentile")
    loss_distribution: List[float] = Field(default_factory=list, description="Monte Carlo loss distribution array")
    per_cve_risk: List[PerCveRiskSummary] = Field(default_factory=list, description="Per-CVE LEF and expected loss magnitude for Layer 5")
    p10: Optional[float] = Field(None, description="10th percentile of annual loss distribution")
    p50: Optional[float] = Field(None, description="50th percentile / median of annual loss distribution")
    p90: Optional[float] = Field(None, description="90th percentile of annual loss distribution")
    p99: Optional[float] = Field(None, description="99th percentile of annual loss distribution")


class OptimizationResults(BaseModel):
    job_id: str
    budget: float = Field(..., description="Remediation budget constraint")
    selected_cves: List[str] = Field(default_factory=list, description="Selected CVE IDs for patching")
    total_cost: float = Field(..., description="Total cost of selected patches")
    post_opt_eal: float = Field(..., description="Post-optimization Expected Annual Loss")
    post_opt_var_95: float = Field(..., description="Post-optimization VaR 95%")
    post_opt_cvar_95: float = Field(..., description="Post-optimization CVaR 95%")
    delta_eal_per_cve: Dict[str, float] = Field(default_factory=dict, description="EAL reduction per selected CVE")
