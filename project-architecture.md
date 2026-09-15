┌──────────────────────────────────────────────────────────────────┐
│ LAYER 1 — INGESTION (async, verified format)                       │
│  Primary: Nessus XML (.nessus) — schema verified in our research   │
│  Stretch: Trivy JSON (only if time remains)                        │
│  POST /scan/upload → returns job_id instantly                      │
│  Background parse → status: PARSED | INGESTION_FAILED              │
└──────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 2 — ENRICHMENT (pre-seeded, zero live calls during demo)      │
│  Local DB, pre-loaded: ~5,000 CVEs × {CVSS, EPSS, KEV}              │
│  Found → full data. Not found → EPSS=0.001, KEV=false, PARTIAL flag│
│  * Note: Layer 2 uses SQLite (app.db) for the internal-round demo, │
│  a deliberate deviation from the originally planned PostgreSQL,    │
│  chosen for zero-dependency demo reliability (no external DB      │
│  service to fail during judging). Schema and query logic are       │
│  portable to PostgreSQL without architecture changes if needed for  │
│  the full SIH round.                                              │
└──────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 3 — RISK CALIBRATION (our modeling layer, honestly labeled)   │
│                                                                    │
│  TCap  = exploit maturity score: KEV=true→1.0, else EPSS value     │
│  RS    = organizational baseline defense score (0–1, config input) │
│  Vuln  = TCap / (TCap + RS)          ← simple, defensible ratio    │
│  TEF   = base contact rate × asset internet-exposure factor        │
│  LEF   = TEF × Vuln                  ← this step IS FAIR-structural│
│                                                                    │
│  Primary Loss   ~ LogNormal(μ,σ)     ← IBM-calibrated              │
│  Secondary Loss = Primary Loss × 0.4  ← IBM cost-category ratio    │
│  Loss Magnitude = Primary + Secondary                              │
└──────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 4 — MONTE CARLO ENGINE (simple, synchronous, fast)            │
│  N ~ Poisson(λ=ΣLEF)  |  X ~ LogNormal per event                    │
│  S = ΣXᵢ, vectorized NumPy, 100,000 iterations (~milliseconds)      │
│  No ProcessPoolExecutor by default — add only if profiling proves  │
│  it's needed (documented as future scalability note, not built)    │
│  Output: EAL, VaR₉₅, CVaR₉₅ + distribution → SIMULATION_FAILED     │
│  state on error, dashboard shows "recalculating," never crashes    │
└──────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 5 — OPTIMIZATION (patch-level, analytically tractable)        │
│  Per CVE-k:  ΔEAL_k = LEF_k × E[LossMagnitude_k]                   │
│  Cost_k = effort tier by CVSS severity (Critical=40h, High=16h,     │
│           Medium=8h, Low=4h) × team hourly rate                     │
│  PuLP 0/1 Knapsack: maximize ΣΔEAL_k·x_k, s.t. ΣCost_k·x_k ≤ Budget│
│  Chosen set → re-simulate once → final EAL/VaR/CVaR₉₅ for dashboard│
│  Solver fails → OPTIMIZATION_UNAVAILABLE, risk numbers still shown │
└──────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 6 — DASHBOARD                                                 │
│  KPI cards: EAL, VaR₉₅, CVaR₉₅ (with ranges, not bare numbers)      │
│  Loss Exceedance Curve: before vs. after optimization                │
│  Ranked patch list by ΔEAL per rupee spent                          │
└──────────────────────────────────────────────────────────────────┘