# Project Build Plan & Layer Specification

## Overview
Continuous Cyber Risk Quantification & Investment Optimization Platform using FAIR modeling and Monte Carlo simulation.

## Architectural Layers
- **Layer 1 — Ingestion**: Parses Nessus XML (`.nessus`) scan reports asynchronously into parsed vulnerability models.
- **Layer 2 — Enrichment**: Enriches CVE data with local pre-loaded database containing CVSS base scores, EPSS probabilities, and CISA KEV flags.
- **Layer 3 — Risk Calibration**: Models threat capability (TCap), defense resistance (RS), vulnerability ratio (Vuln), threat event frequency (TEF), loss event frequency (LEF), and LogNormal loss magnitude distributions.
- **Layer 4 — Monte Carlo Engine**: Runs fast, vectorized NumPy simulations to compute EAL (Expected Annual Loss), VaR95 (Value at Risk at 95th percentile), and CVaR95 (Conditional VaR).
- **Layer 5 — Optimization**: Uses PuLP 0/1 Knapsack optimization to select remediation patches maximizing risk reduction ($\Delta\text{EAL}$) within a given budget.
- **Layer 6 — Dashboard**: React/Recharts interface providing executive KPIs, loss exceedance curves, and ranked patch investment recommendations.
