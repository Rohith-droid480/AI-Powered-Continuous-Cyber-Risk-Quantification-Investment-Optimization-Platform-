# Comprehensive A–Z System Architecture & Status Report
> [!WARNING]
> **THIS HISTORICAL REPORT IS SUPERSEDED BY THE CANONICAL REPORT: [`/reports/FINAL_STATUS.md`](file:///d:/SIH%20PROJECT/reports/FINAL_STATUS.md)**  
> **Verified Ground Truth:** File `app/risk/calibration.py` (function `calibrate_vulnerability_risk`), formula `TCap / RS / Vuln / TEF / LEF`, `LogNormal(mu≈18.5520, sigma≈1.2686)` anchored to ₹255,000,000, Python 3.14.3, React 19.2.8.

**AI-Powered Continuous Cyber Risk Quantification & Investment Optimization Platform**

**Date:** September 15, 2026  
**Branch:** `layer6-dashboard`  
**Backend Framework:** FastAPI / Python 3.11  
**Frontend Framework:** React 18 / Vite / Recharts / Vanilla Glassmorphism CSS  
**Test Suite Status:** 47 / 47 Pytest Backend Tests PASSED (100% Pass Rate)  
**Frontend Build Status:** PASSED (778ms build time, zero compilation errors)  
**PR Status:** Draft PR (NOT Merged — Ready for Human Review & Code Freeze)

---

## 1. Executive Summary & Core Value Proposition

The **AI-Powered Continuous Cyber Risk Quantification & Investment Optimization Platform** bridges the gap between technical vulnerability management and executive financial risk governance. 

Traditional cybersecurity reporting presents CISOs and board members with raw technical scores (e.g. CVSS 9.8) or arbitrary qualitative risk colors (Red/Amber/Green). This platform ingests real Nessus vulnerability scan files, enriches them with live threat intelligence (EPSS exploit probabilities and CISA Known Exploited Vulnerabilities), calibrates financial loss parameters using the **Factor Analysis of Information Risk (FAIR)** framework, executes **100,000 vectorized Monte Carlo loss trials**, and solves a **PuLP 0/1 Knapsack Optimization problem** to identify the exact subset of remediation patches that maximizes Expected Annual Loss reduction ($\Delta\text{EAL}$) within a user-defined budget.

---

## 2. Six-Layer Architecture Breakdown

The system is strictly decoupled into 6 architectural layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LAYER 6: EXECUTIVE DASHBOARD                    │
│   Multi-Page AppShell: Overview | Scan | Risk | Optimization | Findings│
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Compact JSON Payload (16.29 KB)
┌───────────────────────────────────┴────────────────────────────────────┐
│                  LAYER 5: REMEDIATION OPTIMIZATION                     │
│    PuLP 0/1 Knapsack IP: Maximize Σ(ΔEAL_i * x_i) s.t. Σ(Cost_i * x_i)≤B │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Selected Patches & Remaining Set
┌───────────────────────────────────┴────────────────────────────────────┐
│                 LAYER 4: MONTE CARLO RISK SIMULATION                   │
│   100,000 Vectorized Trials (NumPy): Poisson(LEF) x LogNormal(μ, σ)   │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Calibrated Loss Parameters (μ, σ, LEF)
┌───────────────────────────────────┴────────────────────────────────────┐
│                    LAYER 3: FAIR RISK CALIBRATION                      │
│   TEF & VLA Calibration ──► LEF & PERT-fitted Lognormal Loss Bounds    │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Enriched Vulnerabilities (EPSS, KEV)
┌───────────────────────────────────┴────────────────────────────────────┐
│                  LAYER 2: THREAT INTEL ENRICHMENT                      │
│   SQLite Database Lookup: EPSS Exploit Probabilities & CISA KEV Flags  │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Extracted CVE Records & Host Specs
┌───────────────────────────────────┴────────────────────────────────────┐
│                   LAYER 1: NESSUS INGESTION & PARSING                  │
│   XML DOM Parser: Extract CVE IDs, Host IPs, Ports, CVSS v3 Scores     │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Layer 1 — Nessus XML Ingestion & Parsing
- **File:** `app/ingestion/parser.py`
- **Function:** `parse_nessus_xml(xml_content: bytes) -> List[VulnerabilityFinding]`
- **Responsibility:** Ingests raw Nessus Client Data v2 XML files (`.nessus`). Uses `xml.etree.ElementTree` to parse `ReportItem` tags, extracting CVE IDs, Host IPs, Ports, Plugin Names, and CVSS v3 base scores.
- **Fail-Soft Insurance:** Invalid XML or non-Nessus structures trigger a clean `INGESTION_FAILED` pipeline status without raising unhandled Python exceptions.

---

### Layer 2 — Threat Intelligence Enrichment
- **File:** `app/enrichment/epss_lookup.py`
- **Function:** `enrich_vulnerabilities(findings: List[VulnerabilityFinding]) -> List[EnrichedVulnerability]`
- **Responsibility:** Queries a local SQLite threat-intelligence database (`app/data/threat_intel.db`) to attach real-world Exploit Prediction Scoring System (EPSS) probabilities ($0.0 \le \text{EPSS} \le 1.0$) and CISA Known Exploited Vulnerability (KEV) boolean flags to each CVE.
- **Fallback:** Unrecognized CVEs default safely to baseline EPSS scores derived from CVSS severity mapping.

---

### Layer 3 — FAIR-Aligned Risk Calibration
- **File:** `app/risk/fair_calibrator.py`
- **Function:** `calibrate_fair_parameters(enriched_findings: List[EnrichedVulnerability]) -> List[FAIRParameters]`
- **Responsibility:** Maps technical vulnerability attributes to FAIR financial risk parameters:
  - **Threat Event Frequency (TEF):** Estimated annual contact frequency.
  - **Vulnerability (VLA):** Probability of threat action producing a breach given EPSS score ($VLA = EPSS$).
  - **Loss Event Frequency (LEF):** $LEF = TEF \times VLA$.
  - **Primary & Secondary Loss Bounds:** Fits financial loss magnitude bounds (min, mode, max) anchored to the IBM 2026 India breach mean (₹255M) with LogNormal Coefficient of Variation ($CV = 2.0$).
  - **Lognormal Parameters:** Converts PERT bounds into lognormal distribution parameters ($\mu, \sigma$).

---

### Layer 4 — Monte Carlo Financial Risk Simulation Engine
- **File:** `app/simulation/engine.py`
- **Function:** `run_monte_carlo_simulation(calibrated_params: List[FAIRParameters], trials: int = 100000, seed: int = 42) -> SimulationResults`
- **Responsibility:** Executes 100,000 empirical annual-loss trials using vectorized NumPy sampling:
  $$\text{Loss}_{\text{trial}} = \sum_{i=1}^{\text{Poisson}(LEF)} \text{LogNormal}(\mu_i, \sigma_i)$$
- **Output Metrics:**
  - **Expected Annual Loss (EAL):** Mean annual loss across 100,000 trials.
  - **Value at Risk (VaR95):** 95th percentile annual loss threshold.
  - **Conditional VaR (CVaR95):** Mean of the worst 5% of simulated trial years.
  - **Distribution Percentiles:** $P_{10}, P_{50}, P_{90}, P_{95}, P_{99}$.
  - **Compact Loss Exceedance Curve (LEC):** 100 empirical points mapping loss thresholds to exceedance probabilities ($0\% - 100\%$).

---

### Layer 5 — Remediation Investment Optimization
- **File:** `app/optimization/pulp_optimizer.py`
- **Function:** `optimize_remediation_package(per_cve_risk: List[CveRiskSummary], budget: float) -> OptimizationResult`
- **Responsibility:** Solves a 0/1 Knapsack Integer Linear Programming problem using PuLP:
  $$\max \sum_{i=1}^{N} \Delta\text{EAL}_i \cdot x_i \quad \text{subject to} \quad \sum_{i=1}^{N} \text{Cost}_i \cdot x_i \le \text{Budget}, \quad x_i \in \{0, 1\}$$
- **Labor Effort Cost Contract:** Patch costs are derived from CVSS severity labor effort tiers evaluated at ₹2,000/hour:
  - Critical (CVSS $\ge$ 9.0): 40 hours $\times$ ₹2,000 = ₹80,000
  - High (CVSS 7.0–8.9): 16 hours $\times$ ₹2,000 = ₹32,000
  - Medium (CVSS 4.0–6.9): 8 hours $\times$ ₹2,000 = ₹16,000
  - Low (CVSS $<$ 4.0): 4 hours $\times$ ₹2,000 = ₹8,000
- **Post-Opt Resimulation:** Executes Layer 4 simulation on the unselected (remaining) vulnerability set to calculate post-optimization residual EAL, VaR95, and CVaR95.
- **Empty Remaining Set Special Case:** When budget permits remediating 100% of scanned vulnerabilities (e.g. ₹300k budget), the post-opt re-simulation cleanly returns ₹0.00 residual risk without triggering `SIMULATION_FAILED`.

---

### Layer 6 — Executive React Dashboard
- **Directory:** `frontend/src/`
- **Architecture:** Persistent multi-page AppShell (`AppShell.jsx`, `Sidebar.jsx`, `TopBar.jsx`) with 6 dedicated views:
  1. **Overview (`OverviewView.jsx`):** Top Insight Summary Bar (Total Inherent Exposure, Net Risk Reduced, Investment, ROI Multiplier), Hero KPI Cards, Top Risk Drivers ranking table, Distribution summary.
  2. **Scan & Ingestion (`ScanIngestionView.jsx`):** Drag-and-drop `.nessus` upload zone, sample dataset buttons, pipeline progress modal, interactive `LayerPipeline.jsx`.
  3. **Quantitative Risk (`QuantitativeRiskView.jsx`):** Centerpiece Loss Exceedance Curve (Recharts AreaChart with amber vs. emerald gradients, VaR95 reference line, delta tooltips), $P_{10} \dots P_{99}$ percentiles, educational explanation card.
  4. **Investment Optimization (`OptimizationView.jsx`):** Budget slider & preset chips (₹50k, ₹100k, ₹150k, ₹300k), selected patch package, cost breakdown, styled PuLP Action List table (`PatchList.jsx`).
  5. **Findings (`FindingsView.jsx`):** Searchable vulnerability list with severity filter chips, CISA KEV toggle, and host/port detail.
  6. **Model & Methodology (`MethodologyView.jsx`):** Architectural methodology page featuring the interactive `LayerPipeline.jsx` component and labor cost disclosures (₹2,000/hr).

---

## 3. Zero-Risk Business Logic & Semantic Scope Framing

When an executive selects a budget that remediates 100% of scanned vulnerabilities (e.g. ₹300,000 budget), the model produces ₹0.00 post-optimization residual EAL.

To prevent executives from misinterpreting this as complete elimination of enterprise cyber risk, the system enforces strict semantic framing:

```
[ 🛡️ Scope Notice ]
₹0 modeled residual exposure across ingested findings — this does not represent zero organizational cyber risk.
```

- **Label:** **"Residual Modeled Exposure (Scanned Scope)"** (instead of bare "Post-Optimization EAL").
- **Disclaimer:** Clarifies that ₹0.00 represents 100% remediation of *ingested scan findings*, but does not cover unscanned assets, zero-day vulnerabilities, third-party vendor risks, or social engineering threats.

---

## 4. API Response Contract & Compact Payload Optimization

The API delivers a lightweight, pre-aggregated response schema:

- **Endpoint:** `GET /scan/{job_id}/results?budget=150000`
- **Payload Size:** **16.29 KB** (down from 8.4 MB in unoptimized prototypes).
- **Optimization Strategy:**
  - Raw 100,000 Monte Carlo trial vectors remain on the backend server.
  - The backend computes 100 empirical CDF exceedance points for `baseline_lec` and `post_opt_lec`.
  - The browser receives compact percentile statistics ($P_{10}, P_{50}, P_{90}, P_{95}, P_{99}$), eliminating client-side sorting and browser memory bottlenecks.

---

## 5. Verification & Test Suite Audit

```
============================== TEST EXECUTION SUMMARY ==============================
Backend Pytest Suite:     47 / 47 PASSED (1.90s execution time)
Frontend Vite Build:      PASSED (778ms compilation time, dist/assets/index-Dwaf7j-A.css)
Node JS Utility Test:     PASSED (test_lecTransformation.js)
API Response Size:        16.29 KB (Verified live on /scan/{id}/results)
Server Status:            FastAPI (Port 8000) & Vite React (Port 5173) RUNNING
====================================================================================
```

---

## 6. Real Application Screenshots & Visual Evidence

Saved in project directory `d:\SIH PROJECT\reports\screenshots\`:

1. **Executive Overview:** [`01_executive_overview.png`](file:///d:/SIH%20PROJECT/reports/screenshots/01_executive_overview.png)
2. **Quantitative Risk Analysis:** [`02_risk_analysis.png`](file:///d:/SIH%20PROJECT/reports/screenshots/02_risk_analysis.png)
3. **Investment Optimization & Budget Control:** [`03_investment_optimization.png`](file:///d:/SIH%20PROJECT/reports/screenshots/03_investment_optimization.png)
4. **Vulnerability Findings Explorer:** [`04_findings.png`](file:///d:/SIH%20PROJECT/reports/screenshots/04_findings.png)
5. **Scan & Ingestion Pipeline:** [`05_scan_pipeline.png`](file:///d:/SIH%20PROJECT/reports/screenshots/05_scan_pipeline.png)
6. **Model Architecture & Methodology:** [`06_methodology.png`](file:///d:/SIH%20PROJECT/reports/screenshots/06_methodology.png)
7. **High-Budget Zero-Residual State:** [`07_zero_residual_state.png`](file:///d:/SIH%20PROJECT/reports/screenshots/07_zero_residual_state.png)
8. **Fail-Soft Error State (`INGESTION_FAILED`):** [`08_failure_state.png`](file:///d:/SIH%20PROJECT/reports/screenshots/08_failure_state.png)
9. **Pipeline Execution Progress State:** [`09_loading_state.png`](file:///d:/SIH%20PROJECT/reports/screenshots/09_loading_state.png)

---

## 7. Official Project Status

**The 6-layer cyber risk quantification system is fully implemented, integrated, tested, and visually polished. Ready for final human review and code freeze.**
