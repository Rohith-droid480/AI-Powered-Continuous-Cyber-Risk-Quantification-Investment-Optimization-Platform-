# Milestone Report: Layer 1 & 2 Integration — Scan Ingestion & Vulnerability Enrichment

**Date/time completed:** 2026-09-13T23:25:00+05:30  
**Built by:** Beta (Layer 1 & 2 Integration Owner)  
**Branch/commit:** `layer2-enrichment` (`ea3dc0d`)  

---

### 1. What was built (plain language, 3–5 sentences)
This milestone connects Layer 1 (Nessus XML Ingestion) and Layer 2 (CVE Database Enrichment) into an end-to-end automated pipeline. When a user uploads a `.nessus` scan file via `POST /scan/upload`, the background worker parses the raw XML into `ParsedVulnerability` records and immediately opens a managed database session using a clean context manager. Each vulnerability is queried against the pre-seeded local CVE database to attach its CVSS severity score, EPSS exploitation probability, and CISA KEV exploitation flag, transforming it into an `EnrichedVulnerability`. The API endpoint `GET /scan/{job_id}/vulnerabilities` now directly serves `List[EnrichedVulnerability]`, providing the exact enriched data contract required downstream by Layer 3 (Risk Calibration) and Layer 4 (Monte Carlo Simulation).

---

### 2. Inputs and outputs (exact schema)

#### Input:
- Nessus Client Data XML file uploaded as multipart form-data to `POST /scan/upload`.
- Intermediate parsed model (`ParsedVulnerability` in `app/schemas/models.py`):
```python
class ParsedVulnerability(BaseModel):
    cve_id: str = Field(..., description="CVE identifier, e.g. CVE-2021-44228")
    plugin_id: str = Field(..., description="Nessus plugin ID")
    plugin_name: str = Field(..., description="Nessus plugin name")
    host: str = Field(..., description="Target host IP or hostname")
    port: int = Field(0, description="Port number")
    protocol: str = Field("tcp", description="Network protocol")
    severity: int = Field(0, description="Nessus raw severity (0-4)")
    description: Optional[str] = Field(None, description="Vulnerability description")
```

#### Output:
- Endpoint: `GET /scan/{job_id}/vulnerabilities` with `response_model=List[EnrichedVulnerability]`
- Enriched vulnerability schema (`EnrichedVulnerability` in `app/schemas/models.py`):
```python
class EnrichmentStatus(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"

class EnrichedVulnerability(ParsedVulnerability):
    cvss_score: float = Field(0.0, ge=0.0, le=10.0, description="CVSS base score")
    epss_score: float = Field(0.001, ge=0.0, le=1.0, description="EPSS score")
    is_kev: bool = Field(False, description="Known Exploited Vulnerability flag")
    enrichment_status: EnrichmentStatus = Field(EnrichmentStatus.PARTIAL, description="Enrichment status: FULL or PARTIAL")
```

#### Failure States:
- **`INGESTION_FAILED`**: Triggered when the uploaded XML is corrupted, missing required tags, or empty. The job transitions cleanly to `JobStatusEnum.INGESTION_FAILED`, leaving no open database sessions, and `GET /scan/{job_id}/vulnerabilities` returns an empty array `[]`.
- **`PARTIAL` Enrichment**: Triggered for any CVE ID not present in the local database. Returns `cvss_score=0.0`, `epss_score=0.001`, `is_kev=False`, and `enrichment_status=EnrichmentStatus.PARTIAL`.

---

### 3. Tests run and actual results (numerical verification)

All 34 automated unit and integration tests passed in **0.74s**.

#### Integration Tests (`app/tests/test_l1_l2_integration.py`):
1. **End-to-End Pipeline Execution (`test_layer1_layer2_end_to_end_integration`)**:
   - **Action**: Uploaded `/sample-data/enterprise_perimeter_scan.nessus` to `POST /scan/upload`.
   - **Polling**: `GET /scan/{job_id}/status` polled until `PARSED` received.
   - **Findings Count**: Exactly **5** enriched vulnerability records returned.
   - **CVE-2021-44228 Hand-Computed Check**:
     - Expected: `enrichment_status == "FULL"`, `cvss_score == 10.0`, `epss_score == 0.97`, `is_kev == True`
     - Actual: `enrichment_status = FULL`, `cvss_score = 10.0`, `epss_score = 0.97`, `is_kev = True` ✓
     - Context preserved: `host = "192.168.1.10"`, `port = 443`, `protocol = "tcp"`, `plugin_id = "156014"` ✓

2. **Additional CVEs and Fail-Soft Validation (`test_layer1_layer2_additional_cves_and_failsoft`)**:
   - **CVE-2021-41773 Check**: `enrichment_status = FULL`, `cvss_score = 7.5`, `epss_score = 0.80`, `is_kev = True` ✓
   - **Malformed Scan Fail-Soft**: Uploaded `/sample-data/malformed_corrupt.nessus`.
     - Status returned: `INGESTION_FAILED` with clean syntax error message.
     - `GET /scan/{job_id}/vulnerabilities` returned `[]`.
     - Zero unhandled 500 exceptions, zero server crashes ✓.

---

### 3.5. How to test this yourself, manually

1. Open PowerShell in `d:\SIH`.
2. Seed the local database:
   ```powershell
   & "C:\Users\Dilip Shekar K\anaconda3\python.exe" -m app.enrichment.seed_cves
   ```
3. Run the complete test suite:
   ```powershell
   & "C:\Users\Dilip Shekar K\anaconda3\python.exe" -m pytest app/tests/test_l1_l2_integration.py -v
   ```
   **Expected working output:**
   ```
   app/tests/test_l1_l2_integration.py::test_layer1_layer2_end_to_end_integration PASSED [ 50%]
   app/tests/test_l1_l2_integration.py::test_layer1_layer2_additional_cves_and_failsoft PASSED [100%]
   ======================== 2 passed in 0.64s ========================
   ```
4. **Broken result indicators:**
   - Any test failure showing status `PARTIAL` for `CVE-2021-44228` or mismatched scores.
   - Any server crash when uploading corrupted scan files.

---

### 4. Deviations from PLAYBOOK.md / locked architecture (if any)
None — matches spec exactly.

---

### 5. Claims made in this layer that use words like "verified," "official," or "standard"
- **"CVSS v3.1 base score"** & **"EPSS probability"**: Extracted from local database seeded with known industry values (Log4Shell CVSS 10.0, EPSS 0.97).
- No external calls to live APIs are made.

---

### 6. Open questions / methodological uncertainty
- When Layer 3 connects to this output, vulnerabilities marked `PARTIAL` will enter risk calibration with `epss_score=0.001` (0.1% baseline annual exploitation probability) and `cvss_score=0.0`. This guarantees risk simulation completes without blocking on unscored findings.

---

### 7. What still needs to happen before this layer is demo-ready
- Wiring the output `List[EnrichedVulnerability]` into Layer 3's `calibrate_vulnerability_risk` function to generate calibrated FAIR risk parameters (`CalibratedRiskRecord`), which then feeds Layer 4's Monte Carlo engine.
