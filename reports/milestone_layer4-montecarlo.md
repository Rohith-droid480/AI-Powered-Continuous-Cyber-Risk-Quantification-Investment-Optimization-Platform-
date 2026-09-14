# Milestone Report: Layer 4 — Monte Carlo Simulation Engine

**Date/time completed:** 2026-09-13T20:55:00+05:30  
**Built by:** Beta (Risk Simulation Engineer)  
**Branch/commit:** `layer4-montecarlo` (`b4d01e1`)  

---

### 1. What was built (plain language, 3–5 sentences)
Layer 4 implements the fast, vectorized Monte Carlo simulation engine that evaluates 100,000 trial years of annual cyber breach losses across input assets. For each iteration, event counts are drawn from a Poisson distribution ($\lambda = \sum \text{LEF}_k$), and individual loss magnitudes are sampled from each vulnerability's distinct LogNormal distribution $(\mu_k, \sigma_k)$ with secondary losses applied per event draw ($1.4 \times \text{Primary}$). Annual trial losses are aggregated in C-speed vectorized NumPy operations (`np.bincount`) without any Python per-trial loops. The module outputs Expected Annual Loss (EAL), Value at Risk 95% ($\text{VaR}_{95}$), Conditional Value at Risk 95% ($\text{CVaR}_{95}$), and the complete 100,000-trial loss distribution array.

---

### 2. Inputs and outputs (exact schema)

#### Input Schema (`CalibratedRiskRecord` list from `app/schemas/models.py`)
```python
class CalibratedRiskRecord(BaseModel):
    vulnerability: EnrichedVulnerability
    t_cap: float
    rs: float
    vuln: float
    tef: float
    lef: float
    primary_loss_mu: float
    primary_loss_sigma: float
    expected_primary_loss: float
    expected_secondary_loss: float
    expected_loss_magnitude: float
```

#### Output Schema (`SimulationResults` from `app/schemas/models.py`)
```python
class SimulationResults(BaseModel):
    job_id: str
    eal: float = Field(..., description="Expected Annual Loss")
    var_95: float = Field(..., description="Value at Risk at 95th percentile")
    cvar_95: float = Field(..., description="Conditional Value at Risk at 95th percentile")
    loss_distribution: List[float] = Field(default_factory=list)
    per_cve_risk: List[PerCveRiskSummary] = Field(default_factory=list)
```

#### Failure State (`JobStatus` with `SIMULATION_FAILED`)
```python
class JobStatus(BaseModel):
    job_id: str
    status: JobStatusEnum = JobStatusEnum.SIMULATION_FAILED
    message: Optional[str]
```
- Triggered when: `risk_records` is empty or `None`, or contains negative LEF / non-finite $\mu$ or $\sigma$. Returns clean `JobStatus` object without crashing.

---

### 3. Tests run and actual numerical results (verification)

1. **Code Inspection Test (`test_vectorization_requirement_code_inspection`)**:
   - Source code inspected: Verified `VECTORIZATION REQUIREMENT` comment present, `RandomState` absent, and zero per-trial Python for-loops (`for i in range(num_iterations)`). Passed ✓.

2. **Primary Validation Test — Single Vulnerability (`test_layer4_single_vuln_primary_validation`)**:
   - Input: Single Log4j vulnerability with $\text{LEF} = 0.5$ events/year, $\mu = 18.552055, \sigma = 1.268636$, $E[\text{Loss}] = \text{₹}357,000,000$.
   - Analytical Expected EAL: $0.5 \times \text{₹}357,000,000 = \text{₹}178,500,000.00$.
   - Simulated Output (`seed=42`, 100,000 trials):
     - **Simulated EAL**: **₹182,097,849.61** (diff +2.02%, within $\pm 3\%$ tolerance band) ✓
     - **$\text{VaR}_{95}$**: **₹1,029,915,283.47**
     - **$\text{CVaR}_{95}$**: **₹2,109,240,652.18**

3. **Multi-Vulnerability Parameter Aggregation Test (`test_layer4_multi_vulnerability_aggregation`)**:
   - Input: 2 vulnerabilities with distinct parameters:
     - Vuln 1: $\text{LEF}_1 = 0.5$, $\text{EAL}_1 = \text{₹}178,500,000.00$
     - Vuln 2: $\text{LEF}_2 = 0.2$, $\text{EAL}_2 = \text{₹}13,998,427.59$
     - Analytical Total EAL: **₹192,498,427.59**
   - Simulated Output (`seed=42`, 100,000 trials):
     - **Simulated EAL**: **₹194,034,647.12** (diff +0.80%, within $\pm 3\%$ tolerance band) ✓
     - Confirmed `per_cve_risk` contains 2 distinct entries with exact baseline EAL values ✓

4. **Failure State Test (`test_layer4_simulation_failed_state`)**:
   - Empty input list $\rightarrow$ returned `JobStatus(status=SIMULATION_FAILED, message="Input vulnerability list is empty.")` ✓
   - Negative LEF $\rightarrow$ returned `JobStatus(status=SIMULATION_FAILED, message="Invalid record parameters...")` ✓

5. **Event Attribution Ratio Test (`test_layer4_event_attribution_ratio`)**:
   - Refactored to call `engine._simulate_events` directly, directly inspecting internal output arrays:
     - **Total events drawn**: **70,324** events
     - **Events attributed to Vuln 1 ($\text{LEF}_1 = 0.5$)**: **50,123** (**71.27%**)
     - **Events attributed to Vuln 2 ($\text{LEF}_2 = 0.2$)**: **20,201** (**28.73%**)
     - **Empirical ratio ($\text{v1}/\text{v2}$)**: **2.4812** vs expected ratio **2.5000** ($0.5 / 0.2 = 5/2$)
     - **Relative Error**: **0.75%** (well within $\pm 5\%$ statistical tolerance band) ✓

---

### 3.5. How to test this yourself, manually

1. Open a PowerShell terminal in `d:\SIH PROJECT`.
2. Run pytest on the Layer 4 simulation suite:
   ```powershell
   .\venv\Scripts\pytest app/tests/test_layer4_simulation.py -v
   ```
3. Or run this inline Python snippet to execute a 100,000-trial simulation against Layer 3's real output:
   ```powershell
   .\venv\Scripts\python.exe -c "from app.schemas.models import EnrichedVulnerability, EnrichmentStatus; from app.risk.calibration import calibrate_vulnerability_risk; from app.simulation.engine import run_monte_carlo_simulation; v = EnrichedVulnerability(cve_id='CVE-2021-44228', plugin_id='155998', plugin_name='Log4j', host='10.0.0.1', port=80, protocol='tcp', severity=4, description='RCE', cvss_score=10.0, epss_score=0.97, is_kev=True, enrichment_status=EnrichmentStatus.FULL); rec = calibrate_vulnerability_risk(v, rs=0.5, base_contact_rate=1.5, exposure_factor=0.5); res, _ = run_monte_carlo_simulation([rec], num_iterations=100_000, seed=42); print(f'EAL: ₹{res.eal:,.2f} | VaR95: ₹{res.var_95:,.2f} | CVaR95: ₹{res.cvar_95:,.2f}')"
   ```
4. **Expected Output**: `EAL: ₹182,097,849.61 | VaR95: ₹1,029,915,283.47 | CVaR95: ₹2,109,240,652.18`
5. **Broken Output**: Any uncaught exception, or simulated EAL deviating significantly (>5%) from analytical EAL.

---

### 4. Deviations from PLAYBOOK.md / locked architecture (if any)

None — matches spec exactly.

---

### 5. Claims made in this layer that use words like "verified," "official," or "standard"

- **"Vectorized, no legacy RandomState, no per-trial Python loop"**: Verified by AST source code inspection test (`test_vectorization_requirement_code_inspection`) and execution timing benchmarking (<0.3s for 100,000 iterations). `numpy.random.default_rng()` is used exclusively.

---

### 6. Open questions / methodological uncertainty

- **Allocation Approach (Approach A — Poisson Superposition Theorem)**: The engine draws $N \sim \text{Poisson}(\sum \text{LEF}_k)$ for 100,000 trials and assigns each event to vulnerability $k$ with probability $p_k = \frac{\text{LEF}_k}{\sum \text{LEF}}$. Refactored internal helper `_simulate_events` returns `(sampled_vuln_indices, primary_losses, iteration_indices)` directly, and `test_layer4_event_attribution_ratio` asserts on its real returned output.
- **Trial Year Aggregation (`np.bincount`)**: Events are mapped back to trial years via `iteration_indices = np.repeat(np.arange(num_iterations), event_counts)` and aggregated in a single C-speed operation `annual_losses = np.bincount(iteration_indices, weights=event_losses, minlength=num_iterations)`.
- **Secondary Loss Formula Traceability**: Secondary loss is computed per event draw as `secondary_loss = 0.4 * primary_loss` (matching Layer 3's `calculate_secondary_loss` formula exactly), resulting in `total_loss = primary_loss + secondary_loss = 1.4 * primary_loss`.



---

### 7. What still needs to happen before this layer is demo-ready

1. Integration with Layer 5 (PuLP patch optimization engine), which consumes `per_cve_risk` baseline EALs and re-simulates post-optimization risk metrics.
2. Integration with Layer 6 React dashboard to render the Loss Exceedance Curve using `loss_distribution`.
