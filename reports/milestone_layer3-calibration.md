# Milestone Report: Layer 3 — Risk Calibration

**Date/time completed:** 2026-09-13T20:10:00+05:30  
**Built by:** Beta (Risk Calibration Engineer)  
**Branch/commit:** `layer3-calibration` (`00a1ff7`)  

---

### 1. What was built (plain language, 3–5 sentences)
Layer 3 implements the Risk Calibration engine that converts enriched vulnerability data into quantitative loss event frequencies and loss magnitudes measured in Indian Rupees (₹). It calculates Threat Capability (TCap) from active exploitation flags (KEV) or EPSS scores, combines it with organizational Resistance Strength (RS) to derive Vulnerability (Vuln), and computes Loss Event Frequency (LEF = TEF × Vuln). For financial loss magnitude, it calibrates LogNormal distribution parameters $(\mu, \sigma)$ using empirical IBM India data ($\mu_X = \text{₹}255,000,000$) and calculates total Loss Magnitude by incorporating secondary loss exposure. The module operates as pure, deterministic Python functions with zero external database or network dependencies.

---

### 2. Inputs and outputs (exact schema)

#### Input Schema (`EnrichedVulnerability` from `app/schemas/models.py`)
```python
class EnrichedVulnerability(ParsedVulnerability):
    cvss_score: float = Field(0.0, ge=0.0, le=10.0)
    epss_score: float = Field(0.001, ge=0.0, le=1.0)
    is_kev: bool = Field(False)
    enrichment_status: EnrichmentStatus = Field(EnrichmentStatus.PARTIAL)
```

#### Output Schema (`CalibratedRiskRecord` from `app/schemas/models.py`)
```python
class CalibratedRiskRecord(BaseModel):
    vulnerability: EnrichedVulnerability
    t_cap: float = Field(...)
    rs: float = Field(...)
    vuln: float = Field(...)
    tef: float = Field(...)
    lef: float = Field(...)
    primary_loss_mu: float = Field(...)
    primary_loss_sigma: float = Field(...)
    expected_primary_loss: float = Field(...)
    expected_secondary_loss: float = Field(...)
    expected_loss_magnitude: float = Field(...)
```

#### Failure States
- **`ValueError("RS score must be between 0.0 and 1.0 inclusive")`**: Triggered when `rs < 0.0` or `rs > 1.0`. Returns uncaught error / raises exception.
- **`ValueError("Denominator (TCap + RS) must be greater than 0")`**: Triggered when `t_cap + rs <= 0`. Returns uncaught error / raises exception.

---

### 3. Tests run and actual results (numerical verification)

Every Layer 3 function is covered by deterministic hand-computable unit tests in `app/tests/test_layer3_calibration.py`:

- **TCap (Test A — KEV active)**:
  `KEV=true, EPSS=0.25` → expected `1.0` → got `1.0` ✓
- **TCap (Test B — KEV inactive)**:
  `KEV=false, EPSS=0.25` → expected `0.25` → got `0.25` ✓
- **RS (Resistance Strength)**:
  `RS=0.5` → expected `0.5` → got `0.5` ✓
- **Vuln (Vulnerability Ratio)**:
  `TCap=1.0, RS=0.5` → expected `1.0 / (1.0 + 0.5) = 0.666666...` → got `0.6666666666666666` (approx `0.667`) ✓
- **TEF (Threat Event Frequency)**:
  `base_contact_rate=2.0 events/year, exposure_factor=0.5` → expected `1.0 event/year` → got `1.0` ✓
- **LEF (Loss Event Frequency)**:
  `TEF=1.0, Vuln=0.5` → expected `1.0 * 0.5 = 0.5 loss events/year` → got `0.5` ✓
- **Primary Loss Calibration**:
  `mean_loss=₹255,000,000 (IBM India), CV=2.0` → expected $\mu \approx 18.5520, \sigma \approx 1.2686, E[Primary] = \text{₹}255,000,000$ → got $\mu = 18.552067, \sigma = 1.268636, E[Primary] = 255,000,000.0$ ✓
- **Secondary Loss**:
  `primary_loss=₹1,000,000, secondary_ratio=0.4` → expected `₹400,000` → got `400000.0` ✓  
  (Pipeline: `primary_loss=₹255,000,000` → expected `₹102,000,000` → got `102000000.0` ✓)
- **Loss Magnitude**:
  `primary_loss=₹1,000,000, secondary_loss=₹400,000` → expected `₹1,400,000` → got `1400000.0` ✓  
  (Pipeline: `₹255M + ₹102M` → expected `₹357,000,000` → got `357000000.0` ✓)
- **Edge Cases**:
  - `RS = -0.1` and `RS = 1.5` → raised `ValueError` ✓
  - `TCap = 0.0, RS = 0.0` → raised `ValueError` ✓
- **Full Pipeline Schema Validation**:
  - `calibrate_vulnerability_risk(...)` returned valid `CalibratedRiskRecord` matching Pydantic contract exactly ✓

---

### 3.5. How to test this yourself, manually

1. Open PowerShell terminal in `d:\SIH PROJECT`.
2. Run the test command:
   ```powershell
   .\venv\Scripts\pytest app/tests/test_layer3_calibration.py -v
   ```
3. **Expected working output**: All 12 tests pass cleanly in under 0.2 seconds (`12 passed in 0.15s`).
4. **Broken result indicators**: Any test failure showing mismatch in floating-point outputs or schema validation error when building `CalibratedRiskRecord`.

---

### 4. Deviations from PLAYBOOK.md / locked architecture (if any)

None — matches spec exactly.

---

### 5. Claims made in this layer that use words like "verified," "official," or "standard"

No claim of "official FAIR standard" or "canonical FAIR formula" is made for the TCap/RS calibration mapping. The TCap/RS ratio mapping is explicitly documented in code and docstrings as **our modeling assumption**. The `LEF = TEF × Vuln` relationship is tracked as **FAIR-structural**.

---

### 6. Open questions / methodological uncertainty

- **Modeling Assumptions**:
  - The ratio $\text{Vuln} = \frac{\text{TCap}}{\text{TCap} + \text{RS}}$ and the mapping of KEV/EPSS to TCap are our modeling assumptions designed for hackathon tractability and transparency, not canonical FAIR standard formulas.
  - **Primary Loss**: We anchor the mean of our assumed LogNormal primary-loss distribution to IBM's reported 2026 India average total breach cost (₹255,000,000). The dispersion (CV=2.0) and the resulting $\mu \approx 18.5520, \sigma \approx 1.2686$ are our own assumption and mathematical transformation — IBM does not publish a LogNormal mean or these distribution parameters directly.
  - **Secondary Loss**: Secondary Loss = 0.4 × Primary Loss. This 0.4 multiplier is our own conservative illustrative assumption, accounting for additional non-primary costs (regulatory, reputational, customer churn) not fully captured in the primary-loss anchor. It is not derived from an IBM cost-category percentage, and is not specific to DPDPA — DPDPA is only an example of the kind of exposure this margin is meant to cover, not its source.
- **FAIR-Structural**:
  - $\text{LEF} = \text{TEF} \times \text{Vuln}$ is the canonical structural relationship in FAIR risk analysis.


---

### 7. What still needs to happen before this layer is demo-ready

Layer 3 pure functions and unit tests are complete and verified. To be demo-ready, it requires:
1. Integration with Layer 2's live database CVE lookup output (currently verified using mocked `EnrichedVulnerability` objects).
2. Handoff of `CalibratedRiskRecord` parameters to Layer 4 (Monte Carlo simulation engine).
