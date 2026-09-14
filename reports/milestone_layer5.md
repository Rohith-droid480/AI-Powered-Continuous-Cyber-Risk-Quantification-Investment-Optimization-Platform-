# Milestone Report: Layer 5 — Patch Investment Optimization Engine

**Date/time completed:** 2026-09-14T22:10:00+05:30  
**Built by:** Antigravity (Implementation Executor)  
**Branch/commit:** `layer5-optimization`  

---

### 1. What was built (plain language, 3–5 sentences)
Layer 5 implements the Patch Investment Optimization engine using PuLP's 0/1 Knapsack Integer Linear Programming solver. Given a finite remediation budget, the optimizer evaluates all input vulnerabilities, calculates their patch effort cost based on CVSS severity tiers (Critical 40h, High 16h, Medium 8h, Low 4h at a default ₹2,000/hr labor rate), and selects the optimal subset of CVEs that strictly maximizes total Expected Annual Loss reduction ($\Delta \text{EAL} = \text{LEF} \times E[\text{Loss Magnitude}]$) under the budget constraint. Following selection, the engine filters out patched CVEs and executes a post-optimization Monte Carlo re-simulation using the existing Layer 4 engine to quantify residual financial risk ($\text{post\_opt\_eal}$, $\text{VaR}_{95}$, $\text{CVaR}_{95}$).

---

### 2. Inputs and outputs (exact schema contracts)

#### Inputs
- `risk_records`: `List[CalibratedRiskRecord]` (from `app/schemas/models.py`)
- `budget`: `float` (remediation budget in INR / ₹)
- `hourly_rate`: `float` (labor rate per hour in INR / ₹, default ₹2,000/hr)
- `job_id`: `str` (job tracking identifier)
- `num_iterations`: `int` (Monte Carlo trial iterations for post-opt re-simulation, default 100,000)
- `seed`: `Optional[int]` (random seed for reproducible re-simulation)

#### Output Schema (`OptimizationResults` from `app/schemas/models.py`)
```python
class OptimizationResults(BaseModel):
    job_id: str
    budget: float = Field(..., description="Remediation budget constraint")
    selected_cves: List[str] = Field(default_factory=list, description="Selected CVE IDs for patching")
    total_cost: float = Field(..., description="Total cost of selected patches")
    post_opt_eal: float = Field(..., description="Post-optimization Expected Annual Loss")
    post_opt_var_95: float = Field(..., description="Value at Risk 95% after remediation")
    post_opt_cvar_95: float = Field(..., description="Conditional VaR 95% after remediation")
    delta_eal_per_cve: Dict[str, float] = Field(default_factory=dict, description="EAL reduction per selected CVE")
```

#### Failure State Schema (`JobStatus` with `OPTIMIZATION_UNAVAILABLE`)
```python
class JobStatus(BaseModel):
    job_id: str
    status: JobStatusEnum = JobStatusEnum.OPTIMIZATION_UNAVAILABLE
    message: Optional[str]
```
- Triggered when: `budget < 0`, `risk_records` is empty/None, `hourly_rate <= 0`, non-finite numerical parameters exist, or solver failures occur.

---

### 3. Tests run and actual numerical results (verification)

1. **Test 1 — Cost Tiers (`test_layer5_patch_cost_calculation_tiers`)**:
   - `hourly_rate = ₹2,000/hr`
   - Critical ($\text{CVSS} \ge 9.0$): 40h $\times 2000 = \mathbf{\text{₹}80,000.00}$ ✓
   - High ($7.0 \le \text{CVSS} < 9.0$): 16h $\times 2000 = \mathbf{\text{₹}32,000.00}$ ✓
   - Medium ($4.0 \le \text{CVSS} < 7.0$): 8h $\times 2000 = \mathbf{\text{₹}16,000.00}$ ✓
   - Low ($\text{CVSS} < 4.0$): 4h $\times 2000 = \mathbf{\text{₹}8,000.00}$ ✓

2. **Test 2 — $\Delta \text{EAL}$ Knapsack Optimization (`test_layer5_delta_eal_knapsack_optimization`)**:
   - 3 Toy CVEs:
     - CVE-A: cost = ₹80,000, $\Delta \text{EAL} = \text{₹}100,000,000.00$
     - CVE-B: cost = ₹32,000, $\Delta \text{EAL} = \text{₹}60,000,000.00$
     - CVE-C: cost = ₹16,000, $\Delta \text{EAL} = \text{₹}20,000,000.00$
   - Budget constraint: **₹96,000.00**
   - Optimal Knapsack selection: `['CVE-A', 'CVE-C']`
   - Total Cost: **₹96,000.00** ($\le$ ₹96,000.00 budget)
   - Total Selected $\Delta \text{EAL}$: **₹120,000,000.00** ✓

3. **Test 3 — Failure State (`test_layer5_optimization_failure_states`)**:
   - `budget = -5000` $\rightarrow$ returned `JobStatus(status=OPTIMIZATION_UNAVAILABLE, message="Remediation budget cannot be negative...")` ✓
   - empty risk list $\rightarrow$ returned `JobStatus(status=OPTIMIZATION_UNAVAILABLE, message="Input risk records list is empty.")` ✓

4. **Test 4 — Post-Optimization Re-simulation (`test_layer5_post_optimization_resimulation`)**:
   - Filtered out selected CVEs, re-simulated unpatched remaining CVEs using Layer 4 Monte Carlo engine.
   - Populated `post_opt_eal`, `post_opt_var_95`, and `post_opt_cvar_95` correctly ✓.

5. **Test 5 — Objective Traceability (`test_layer5_objective_traceability_not_cvss`)**:
   - CVE-HIGH-CVSS (CVSS 10.0, cost ₹80k, $\Delta \text{EAL} = \text{₹}10\text{M}$)
   - CVE-HIGH-DEAL (CVSS 5.0, cost ₹16k, $\Delta \text{EAL} = \text{₹}100\text{M}$)
   - Budget = ₹50,000.00
   - Optimizer selected `['CVE-HIGH-DEAL']` (higher $\Delta \text{EAL}$), ignoring higher CVSS score ✓.

6. **Test 6 — Real-Data Integration (`test_layer5_real_data_integration`)**:
   - Executed on `sample-data/enterprise_perimeter_scan.nessus`.
   - Selected `['CVE-2008-5161', 'CVE-2020-1472', 'CVE-2021-41773']` at cost ₹120,000.00 ($\le$ ₹150,000 budget).

---

### 4. Real-Data Optimization Results (`sample-data/enterprise_perimeter_scan.nessus`)

- **Demo Budget:** ₹150,000.00
- **Input CVE Count:** 5
- **Selected CVEs:** `CVE-2008-5161`, `CVE-2020-1472`, `CVE-2021-41773`
- **Total Selected Patch Cost:** **₹120,000.00**
- **Total Selected Analytical $\Delta \text{EAL}$:** **₹489,730,769.23** (₹489.73 Million)
- **Pre-optimization Analytical EAL:** **₹965,730,769.23** (₹965.73 Million)
- **Pre-optimization Simulated EAL:** **₹967,234,205.61** (₹967.23 Million)
- **Analytical Residual EAL:** **₹476,000,000.00** (₹476.00 Million)
- **Post-optimization Simulated EAL:** **₹475,454,244.15** (₹475.45 Million)
- **Post-optimization $\text{VaR}_{95}$:** **₹1,887,895,475.61** (₹1.89 Billion, reduced from ₹3.13B)
- **Post-optimization $\text{CVaR}_{95}$:** **₹3,361,113,758.92** (₹3.36 Billion, reduced from ₹5.03B)
- **Remaining Unpatched CVE Count:** 2 (`CVE-2021-44228`, `CVE-2017-5638`)
- **Optimization + Re-simulation Runtime:** **44.90 ms**
- **Analytical vs Simulated Residual Relative Difference:** **0.1147%**

---

### 5. Deviations from PLAYBOOK.md / locked architecture (if any)

None — matches locked architecture exactly.

---

### 6. Claims made in this layer that use words like "verified", "official", or "standard"

- **"PuLP CBC 0/1 Knapsack Integer Linear Programming"**: PuLP's default CBC solver is used to find the exact global maximum of the 0/1 Knapsack ILP model.
- **"Strict $\Delta \text{EAL}$ Objective"**: Objective is strictly $\sum \Delta \text{EAL}_k \cdot x_k$ where $\Delta \text{EAL}_k = \text{LEF}_k \times E[\text{Loss Magnitude}_k]$. CVSS, EPSS, priority scores, and ROI ratios were NOT used as objectives.

---

### 7. Open questions / methodological uncertainty

- **Analytical vs Stochastic Residual EAL**: Analytical residual EAL ($\text{Pre-EAL} - \sum \Delta \text{EAL}_{\text{selected}} = \text{₹}476.00\text{M}$) matches post-optimization stochastic Monte Carlo re-simulation ($\text{₹}475.45\text{M}$) within 0.11% relative difference.
- **Remediation Cost Tiers**: Labor hours are assigned by CVSS score (40h, 16h, 8h, 4h) at a constant ₹2,000/hr. These tier boundaries are modeling choices.

---

### 8. What still needs to happen before this layer is demo-ready

1. Integration into FastAPI `/optimization/solve` endpoint.
2. Integration with Layer 6 React dashboard to render pre- vs post-remediation financial risk charts.

---

ROUTE THIS REPORT → ChatGPT → Claude → ask: "Does the optimizer's objective strictly match the ΔEAL definition (LEF × Expected Loss Magnitude) without inventing a new risk score, and is the 0/1 Knapsack solution mathematically consistent with the budget constraint and the post-optimization re-simulation?"
