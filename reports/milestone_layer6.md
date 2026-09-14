# Milestone Report: Layer 6 — Executive React Dashboard

**Date/time completed:** 2026-09-14T23:15:00+05:30  
**Built by:** Gamma-2 (Frontend Implementation Agent)  
**Branch/commit:** `layer6-dashboard`  

---

### 1. What was built
Layer 6 implements the single-page Executive React Dashboard for the AI-Powered Continuous Cyber Risk Quantification & Investment Optimization Platform. Built with Vite, React 19, and Recharts, the dashboard connects directly to the backend API (`http://localhost:8000`) and presents an executive risk management interface. It includes an Upload Flow for `.nessus` scan files, Executive KPI Cards, an empirical Loss Exceedance Curve (CCDF), a Ranked PuLP 0/1 Knapsack Remediation Table, an interactive Budget Control slider, deliberate loading and fail-soft error states, and a Model Calibration Transparency Disclosure banner.

---

### 2. Why it was built this way
The dashboard is designed to immediately answer the central executive question: *"Where is the organization's cyber risk, and where should we spend the next rupee?"*
- **Single-Page Executive Focus:** Avoided multi-tab fragmentation, complex settings, or authentication bloat.
- **Empirical CCDF Centerpiece:** Loss Exceedance Curve is plotted directly from Monte Carlo simulation output distribution arrays rather than smooth mathematical approximations.
- **Strict Objective Alignment:** Remediation patch ranking displays actual Layer 5 $\Delta \text{EAL}$ values and cost efficiency ($\Delta \text{EAL} / \text{Cost}$) without inventing priority scores or sorting by CVSS severity alone.
- **Fail-Soft Resiliency:** Handles `INGESTION_FAILED`, `SIMULATION_FAILED`, and `OPTIMIZATION_UNAVAILABLE` cleanly without exposing raw Python tracebacks.

---

### 3. Exact files / components changed

- `app/api/main.py`: Updated `GET /scan/{job_id}/results` to execute real Layer 3 risk calibration, Layer 4 Monte Carlo simulation, Layer 5 PuLP optimization, and post-optimization re-simulation when a real job is queried, while maintaining backward-compatible stub fallback for `test_scan_results_stub`.
- `frontend/src/App.jsx`: Assembled main dashboard SPA with API integration, state management, budget controls, and pre-loaded known-good demo dataset preview.
- `frontend/src/index.css`: Custom executive dark design system (`#0b0f19` background, glassmorphism cards, Inter/JetBrains typography, crisp visual hierarchy).
- `frontend/src/components/KPICards.jsx`: Executive KPI metric cards (Baseline EAL, Post-Opt EAL, Risk Reduction %, VaR95, CVaR95, Selected Remediation Cost, Efficiency Ratio).
- `frontend/src/components/LossExceedanceCurve.jsx`: Recharts AreaChart plotting baseline exposure vs post-optimization residual exceedance curves with VaR95 reference lines.
- `frontend/src/components/PatchList.jsx`: Table of ranked remediation decisions displaying CVSS effort tiers, costs, analytical $\Delta \text{EAL}$, and PuLP selection status.
- `frontend/src/components/BudgetControl.jsx`: Interactive budget presets (₹50k, ₹150k, ₹300k) and slider triggering real-time re-optimization.
- `frontend/src/components/UploadFlow.jsx`: Nessus scan file drop zone and quick-run sample buttons.
- `frontend/src/components/ModelAssumptionsBanner.jsx`: Calibration transparency banner detailing FAIR structural contracts, IBM India primary loss anchors, and secondary loss multipliers.
- `frontend/src/utils/lecTransformation.js`: Pure statistical utility deriving empirical exceedance probabilities $P(\text{Loss} \ge S) = \frac{N - i}{N} \times 100\%$ from sorted loss arrays.
- `frontend/src/utils/test_lecTransformation.js`: Node.js unit test suite for empirical CCDF math.

---

### 4. API / Schema contracts used

The dashboard consumes the official backend Pydantic schema contracts:
- `SimulationResults`: `job_id`, `eal`, `var_95`, `cvar_95`, `loss_distribution`, `per_cve_risk`
- `OptimizationResults`: `job_id`, `budget`, `selected_cves`, `total_cost`, `post_opt_eal`, `post_opt_var_95`, `post_opt_cvar_95`, `delta_eal_per_cve`
- `EnrichedVulnerability`: `cve_id`, `plugin_name`, `host`, `port`, `cvss_score`, `epss_score`, `is_kev`, `enrichment_status`

---

### 5. Loss Exceedance Curve (LEC) Methodology & Transformation

The Loss Exceedance Curve represents the empirical Complementary Cumulative Distribution Function (CCDF):
$$P(\text{Loss} \ge S) = \frac{\text{Count of trial years with Loss} \ge S}{N_{\text{trials}}} \times 100\%$$

- **X Axis:** Annual Loss Magnitude $S$ in INR (₹)
- **Y Axis:** Exceedance Probability $P(\text{Loss} \ge S)$ in % (0% to 100%)
- **Baseline vs Residual:** Compares pre-remediation inherent risk curve (amber/orange) against post-remediation residual risk curve (emerald/green).
- **Transformation:** `computeLossExceedancePoints()` sorts the raw 100,000-trial `loss_distribution` array and downsamples it into 60 smooth, monotonic data points for Recharts rendering without mutating original backend data.

---

### 6. Real-Data Verification (`sample-data/enterprise_perimeter_scan.nessus`, Budget = ₹150,000)

When executed against the backend API with the real known-good scan:
- **Parsed CVEs:** 5 (`CVE-2021-44228`, `CVE-2021-41773`, `CVE-2017-5638`, `CVE-2020-1472`, `CVE-2008-5161`)
- **Baseline EAL:** **₹965,730,769.23** (₹965.73 Million)
- **Baseline VaR95:** **₹3,129,621,032.79** (₹3.13 Billion)
- **Baseline CVaR95:** **₹5,033,058,626.55** (₹5.03 Billion)
- **Selected Remediation Patches:** `['CVE-2008-5161', 'CVE-2020-1472', 'CVE-2021-41773']`
- **Total Selected Patch Cost:** **₹120,000.00** ($\le$ ₹150,000.00 budget)
- **Analytical $\Delta \text{EAL}$ Reduction:** **₹489,730,769.23** (₹489.73 Million)
- **Post-Optimization Simulated EAL:** **₹475,454,244.15** (₹475.45 Million, -50.8% reduction)
- **Post-Optimization VaR95:** **₹1,887,895,475.61** (₹1.89 Billion)
- **Post-Optimization CVaR95:** **₹3,361,113,758.92** (₹3.36 Billion)

---

### 7. Tests & Build Results

- **Frontend Production Build (`npm run build`):** **PASSED** in 300ms (built clean production dist bundle).
- **Statistical Transformation Unit Test (`node frontend/src/utils/test_lecTransformation.js`):** **PASSED** (all empirical CCDF and formatting assertions verified).
- **Backend Test Suite (`pytest`):** **45 / 45 PASSED** in 1.22s (0 failures, zero regressions across Layers 1–5).

---

### 8. Loading and Failure-State Verification

- **Processing State:** Shows explicit loading spinners during file upload, parsing, Monte Carlo simulation, and PuLP re-optimization.
- **`INGESTION_FAILED` / Malformed File Test:** Uploading `sample-data/malformed_corrupt.nessus` displays an executive error banner: `INGESTION_FAILED: Failed to parse XML syntax: not well-formed...` without crashing the application.
- **Fail-Soft Design:** Backend failures gracefully report status without raw Python tracebacks in the user interface.

---

### 9. Performance Observations

- **Frontend Bundle Build:** 300 ms
- **Statistical Transformation Runtime:** < 2 ms for 100,000 simulation trials
- **End-to-End API Response:** < 200 ms for complete pipeline execution (Ingestion $\rightarrow$ Enrichment $\rightarrow$ Calibration $\rightarrow$ Monte Carlo $\rightarrow$ PuLP Optimization).

---

### 10. Explicit Confirmations

- **Layer 1–5 Risk Mathematics:** **UNTOUCHED.** All risk formulas, calibration parameters, and Monte Carlo algorithms remain intact.
- **Optimization Objective:** **UNTOUCHED.** Maximizes total $\Delta \text{EAL} = \text{LEF} \times E[\text{Loss Magnitude}]$ under budget; no priority scores or CVSS-only rankings were introduced.
- **Charting Engine:** Uses `recharts` exclusively; no secondary charting libraries added.

---

ROUTE THIS REPORT → Gemini / Kimi → ask: "What is wrong with this Layer 6 dashboard implementation? Check the actual code and test evidence for frontend correctness, API/schema contract mismatches, Loss Exceedance Curve correctness, loading/failure states, and any unnecessary scope or hardcoded data. Do not judge it by appearance alone."
