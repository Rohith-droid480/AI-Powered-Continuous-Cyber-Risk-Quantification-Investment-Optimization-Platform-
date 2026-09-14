# Milestone Report: Real-Data Vertical Integration (Layers 1 → 4)

**Date/time completed:** 2026-09-14T21:45:00+05:30  
**Built by:** Integration Team (Alpha & Beta)  
**Branch/commit:** `integration-l1-l4`  

---

### 1. What was built (plain language, 3–5 sentences)
This milestone proves the P0 real-data vertical integration of Layers 1, 2, 3, and 4 into a single continuous pipeline on an actual `.nessus` scan file (`sample-data/enterprise_perimeter_scan.nessus`). Raw XML vulnerability findings were parsed into Pydantic models (Layer 1), enriched with CVSS, EPSS, and CISA KEV data from the local SQLite database (Layer 2), calibrated using FAIR-aligned Loss Event Frequency and LogNormal Primary/Secondary loss formulas (Layer 3), and processed through the 100,000-iteration vectorized Monte Carlo simulation engine (Layer 4). All layers composed seamlessly without manual mock objects, data fabrications, schema alterations, or loss distribution overrides.

---

### 2. Inputs and outputs (exact schema contracts)

The integration verified the complete object flow across official Pydantic schema contracts:

```
  sample-data/enterprise_perimeter_scan.nessus (Real XML)
        ↓
  Layer 1: parse_nessus_xml()
        ↓ ParsedVulnerability objects
  Layer 2: enrich_vulnerabilities()
        ↓ EnrichedVulnerability objects
  Layer 3: calibrate_vulnerability_risk()
        ↓ CalibratedRiskRecord objects
  Layer 4: run_monte_carlo_simulation(num_iterations=100_000, seed=42)
        ↓ SimulationResults
  [EAL, VaR95, CVaR95, loss_distribution, per_cve_risk]
```

#### Verified Stage Contracts:
1. **Layer 1 Output**: `ParsedVulnerability` (`cve_id`, `plugin_id`, `plugin_name`, `host`, `port`, `protocol`, `severity`, `description`)
2. **Layer 2 Output**: `EnrichedVulnerability` (inherits `ParsedVulnerability` + `cvss_score`, `epss_score`, `is_kev`, `enrichment_status`)
3. **Layer 3 Output**: `CalibratedRiskRecord` (`vulnerability`, `t_cap`, `rs`, `vuln`, `tef`, `lef`, `primary_loss_mu`, `primary_loss_sigma`, `expected_primary_loss`, `expected_secondary_loss`, `expected_loss_magnitude`)
4. **Layer 4 Output**: `SimulationResults` (`job_id`, `eal`, `var_95`, `cvar_95`, `loss_distribution`, `per_cve_risk`)

---

### 3. Real-data vertical slice evidence (actual run metrics)

**Real Input File:** `sample-data/enterprise_perimeter_scan.nessus`

| Stage | Metric / Parameter | Value |
| :--- | :--- | :--- |
| **Layer 1 (Ingestion)** | Parsed vulnerability records | 5 |
| | CVE-bearing findings | 5 (CVE-2021-44228, CVE-2021-41773, CVE-2017-5638, CVE-2020-1472, CVE-2008-5161) |
| **Layer 2 (Enrichment)** | FULL enrichments (seeded CVE lookup) | 5 (100%) |
| | PARTIAL enrichments (fallback) | 0 (0%) |
| **Layer 3 (Calibration)** | Calibrated risk records | 5 |
| | Total Loss Event Frequency ($\sum \text{LEF}$) | **2.7051** events/year |
| | Total Analytical Baseline EAL | **₹965,730,769.23** (₹965.73 Million) |
| **Layer 4 (Monte Carlo)** | Simulation Iterations | 100,000 |
| | Random Seed | 42 |
| | **Simulated EAL** | **₹967,234,205.61** (₹967.23 Million) |
| | **Absolute EAL Difference** | **₹1,503,436.37** |
| | **Relative EAL Difference** | **0.1557%** (well within $\pm 5\%$ sanity threshold) |
| | **Value at Risk 95% ($\text{VaR}_{95}$)** | **₹3,129,621,032.79** (₹3.13 Billion) |
| | **Conditional VaR 95% ($\text{CVaR}_{95}$)** | **₹5,033,058,626.55** (₹5.03 Billion) |
| | `loss_distribution` array length | **100,000** floats |
| **Execution Performance** | Layer 1 Parsing Time | 0.24 ms |
| | Layer 2 Enrichment Time | 110.01 ms |
| | Layer 3 Calibration Time | 0.04 ms |
| | Layer 4 Monte Carlo Engine Time | 42.26 ms |
| | **Total End-to-End Pipeline Time** | **152.56 ms** |
| **Pipeline Status** | Output Status | `COMPLETED` |

---

### 4. Mathematical & Statistical Verification

From the real Layer 3 records:
$$\text{Analytical Baseline EAL} = \sum_{k=1}^5 \left( \text{LEF}_k \times E[\text{Loss Magnitude}_k] \right) = \text{₹}965,730,769.23$$

Comparing analytical expectations against Layer 4 Monte Carlo simulation (`seed=42`, 100,000 iterations):
- Analytical EAL: **₹965,730,769.23**
- Simulated EAL: **₹967,234,205.61**
- Relative Difference: **0.1557%**

This confirms that:
1. No vulnerabilities were dropped or duplicated.
2. LEF values propagated correctly into Poisson draw rates.
3. LogNormal parameters ($\mu, \sigma$) and secondary loss scaling ($1.4 \times \text{Primary}$) were preserved per-vulnerability.
4. Total loss aggregation via `np.bincount` converged within statistical bounds.

---

### 5. Failure State Verification

**Malformed Input File:** `sample-data/malformed_corrupt.nessus`

- Executed against Layer 1 parser and background job manager:
  - Result: `NessusParsingError: Failed to parse XML syntax: not well-formed (invalid token): line 7, column 62`
  - Backend job status transitioned cleanly to `INGESTION_FAILED`.
  - Zero raw tracebacks or unhandled exceptions escaped to the caller.

---

### 6. Full Test Suite Results

Ran complete pytest suite after adding permanent integration test `app/tests/test_l1_l4_integration.py`:
- **Total Tests:** 41 passed
- **Failures:** 0
- **Runtime:** 1.10 seconds
- **Regression:** Zero existing tests regressed.

---

### 7. Scope Guard Audit

- Layer 5 (Patch Investment Optimization / PuLP): **NOT STARTED** (Scope preserved)
- Layer 6 (Executive Dashboard): **NOT STARTED** (Scope preserved)
- Model logic, risk formulas, and statistical simulation engine were **UNTOUCHED**.

---

### 8. How to check this yourself, manually

1. Open PowerShell in `d:\SIH PROJECT`.
2. Run the integration test suite:
   ```powershell
   .\venv\Scripts\pytest app/tests/test_l1_l4_integration.py -v
   ```
3. Run the complete end-to-end pipeline python command on real data:
   ```powershell
   .\venv\Scripts\python -c "import time; from app.ingestion.parser import parse_nessus_xml; from app.enrichment.enrichment import enrich_vulnerabilities; from app.risk.calibration import calibrate_vulnerability_risk; from app.simulation.engine import run_monte_carlo_simulation; xml = open('sample-data/enterprise_perimeter_scan.nessus', 'rb').read(); vulns = parse_nessus_xml(xml); enriched = enrich_vulnerabilities(vulns); records = [calibrate_vulnerability_risk(e) for e in enriched]; res, _ = run_monte_carlo_simulation(records, num_iterations=100000, seed=42); print(f'Parsed: {len(vulns)} | Enriched: {len(enriched)} | Calibrated: {len(records)} | Simulated EAL: INR {res.eal:,.2f} | VaR95: INR {res.var_95:,.2f} | CVaR95: INR {res.cvar_95:,.2f}')"
   ```
4. **Expected Output**:
   `Parsed: 5 | Enriched: 5 | Calibrated: 5 | Simulated EAL: INR 967,234,205.61 | VaR95: INR 3,129,621,032.79 | CVaR95: INR 5,033,058,626.55`

---

ROUTE THIS REPORT → Whole team / human integration review

────────────── COPY EVERYTHING BELOW THIS LINE ──────────────
P0 Real-Data Vertical Integration Checkpoint (Layers 1->4) verified successfully. 
We parsed sample-data/enterprise_perimeter_scan.nessus into 5 ParsedVulnerability objects, enriched them via local SQLite DB into 5 FULL EnrichedVulnerability objects, calibrated FAIR risk records (total LEF = 2.7051 events/year), and executed 100,000-trial Monte Carlo simulation (seed=42). 

Key Results:
- Analytical EAL: ₹965.73M
- Simulated EAL: ₹967.23M (0.1557% relative difference, well within ±5% sanity threshold)
- VaR95: ₹3.13B
- CVaR95: ₹5.03B
- Total Pipeline Runtime: 152.56 ms (Monte Carlo Engine: 42.26 ms)
- Full Test Suite: 41/41 tests passing (1.10s)
- Malformed scan test: Gracefully raises NessusParsingError / INGESTION_FAILED with no unhandled raw exceptions.

Review question: Can the team confirm that the real-data vertical slice produces expected structural and numerical behavior before proceeding to Layer 5 optimization?
────────────────────────────────────────────────────────────
