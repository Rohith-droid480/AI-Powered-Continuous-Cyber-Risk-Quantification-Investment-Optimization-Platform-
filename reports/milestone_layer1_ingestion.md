# Milestone Report: Layer 1 — Ingestion & Nessus XML Parser

**Date/time completed:** 2026-09-13T00:40:00+05:30  
**Built by:** Beta (Layer 1 & 2 Owner)  
**Branch/commit:** `layer1-ingestion` / `78c368c`  

---

### 1. What was built (plain language, 3–5 sentences)
Layer 1 implements the vulnerability ingestion subsystem that consumes Nessus vulnerability scan files (`.nessus` XML format) and normalizes them into structured vulnerability records. An asynchronous job worker handles the upload process via `POST /scan/upload`, returning a unique `job_id` immediately while parsing occurs concurrently in the background. The parser safely processes XML elements and extracts host configurations, network services, raw severities, descriptions, and CVE identifiers mapped directly to the `ParsedVulnerability` contract. If an uploaded scan file is corrupted, malformed, or empty, the engine cleanly catches the parsing exception and transitions the job state to `INGESTION_FAILED` without throwing unhandled exceptions or crashing the server.

---

### 2. Inputs and outputs (exact schema)

#### Input:
- **Nessus XML Document** (`NessusClientData_v2`) provided via multipart file upload to `POST /scan/upload`.
- Relevant payload schema in `app/schemas/models.py`:
```python
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
```

#### Output:
- Immediate API response: `JobStatus` with `status="PROCESSING"` and unique `job_id`.
- Background parsed records: `List[ParsedVulnerability]` conforming to:
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

#### Failure state:
- **`INGESTION_FAILED`** triggered when:
  - The XML file contains invalid or broken syntax (e.g. unclosed tags, malformed characters).
  - The document root is not `<NessusClientData_v2>` or lacks a `<Report>` element.
  - The uploaded file is empty (`0 bytes`) or contains only whitespace.
- **Returns:**
```json
{
  "job_id": "job_9b3e12a45c71",
  "status": "INGESTION_FAILED",
  "message": "Ingestion failed: Failed to parse XML syntax: unclosed token: line 8, column 8"
}
```
HTTP status code: `200 OK` (fail-soft asynchronous job state reporting, zero process crash).

---

### 3. Tests run and actual results (not "tests pass" — show the numbers)

Total automated tests executed: **15 tests (15 passed, 0 failed) in 0.39s**.

#### A. Hand-computable parser unit tests (`app/tests/test_parser.py`):
1. **`test_hand_computed_single_finding`**:
   - **Input**: 1 host (`10.1.1.50`), 1 ReportItem (port 443, tcp, sev 4, plugin 99901, CVE-2024-0001).
   - **Hand-computed expected**: Count = 1, `cve_id="CVE-2024-0001"`, `plugin_id="99901"`, `plugin_name="Hand Computed Test Vulnerability"`, `host="10.1.1.50"`, `port=443"`, `protocol="tcp"`, `severity=4`.
   - **Actual result**: Count = 1, all 8 fields match exact known constants ✓.

2. **`test_enterprise_perimeter_scan_hand_computed`**:
   - **Input**: `/sample-data/enterprise_perimeter_scan.nessus` (2 hosts: `192.168.1.10`, `192.168.1.20`).
   - **Hand-computed expected**:
     - Total findings: 5
     - Severity 4 count: 3 (`CVE-2021-44228`, `CVE-2017-5638`, `CVE-2020-1472`)
     - Severity 3 count: 1 (`CVE-2021-41773`)
     - Severity 1 count: 1 (`CVE-2008-5161`)
     - Host `192.168.1.10` count: 3; Host `192.168.1.20` count: 2
   - **Actual result**: Total = 5, Sev 4 = 3, Sev 3 = 1, Sev 1 = 1, Host10 = 3, Host20 = 2 ✓.

3. **`test_internal_services_scan_hand_computed`**:
   - **Input**: `/sample-data/internal_services_scan.nessus` (1 host: `10.0.0.15`).
   - **Hand-computed expected**: Count = 3 (`CVE-2023-38606`, `CVE-2022-3602`, `CVE-2023-4863`).
   - **Actual result**: Count = 3, exact CVE sequence matches `["CVE-2023-38606", "CVE-2022-3602", "CVE-2023-4863"]` ✓.

4. **`test_malformed_xml_triggers_nessus_parsing_error`**:
   - **Input**: `/sample-data/malformed_corrupt.nessus`.
   - **Expected**: Raises `NessusParsingError` (subclass of `IngestionError`), message contains `"Failed to parse XML syntax"`.
   - **Actual result**: Raised `NessusParsingError`, error caught cleanly without unhandled crash ✓.

5. **`test_empty_or_whitespace_scan` & `test_non_nessus_xml`**:
   - **Input**: `""` and `<Document><Item/></Document>`.
   - **Expected**: `NessusParsingError` with `"empty"` and `"Expected <NessusClientData_v2>"`.
   - **Actual result**: Both raised `NessusParsingError` with expected explanatory messages ✓.

#### B. Async job and API fail-soft tests (`app/tests/test_ingestion_jobs.py`):
1. **`test_job_manager_lifecycle_success`**:
   - **Input**: 1 finding XML via `JobManager.process_scan_job`.
   - **Actual result**: Job status transitions from `PROCESSING` → `PARSED`, `len(parsed_vulnerabilities) == 1`, `cve_id="CVE-2023-9999"` ✓.

2. **`test_job_manager_fail_soft_malformed_xml`**:
   - **Input**: Non-XML bytes `b"<<<THIS IS NOT XML>>>"`.
   - **Actual result**: Job status transitions to `INGESTION_FAILED`, message contains `"Ingestion failed"`, count = 0 ✓.

3. **`test_api_upload_valid_enterprise_scan`**:
   - **Input**: `POST /scan/upload` with `enterprise_perimeter_scan.nessus`.
   - **Actual result**: HTTP 200, `job_id` returned immediately; `GET /scan/{job_id}/status` returns `status="PARSED"`; `GET /scan/{job_id}/vulnerabilities` returns `count=5` with exact CVEs `CVE-2021-44228` and `CVE-2020-1472` ✓.

4. **`test_api_upload_malformed_scan_triggers_ingestion_failed`**:
   - **Input**: `POST /scan/upload` with `malformed_corrupt.nessus`.
   - **Actual result**: HTTP 200, `job_id` returned; `GET /scan/{job_id}/status` returns `status="INGESTION_FAILED"` with descriptive parse error; `GET /scan/{job_id}/vulnerabilities` returns `count=0`; server process remains running with 0 crashes ✓.

---

### 4. Deviations from PLAYBOOK.md / locked architecture (if any)
None — matches spec exactly.

---

### 5. Claims made in this layer that use words like "verified," "official," or "standard"
- **"NessusClientData_v2 XML format"**: Tenable's documented Nessus v2 XML report format containing `<Report>`, `<ReportHost>`, and `<ReportItem>` tags. Source: Tenable Nessus v2 file format specification.
- All other behavior (job lifecycle, fail-soft state transition, error formatting) is our implementation design adhering to the locked project architecture.

---

### 6. Open questions / things the author is unsure about
- If a single Nessus `<ReportItem>` contains multiple `<cve>` entries (e.g. Apache vulnerabilities with multiple CVEs), the parser currently emits one `ParsedVulnerability` record per CVE with duplicated host/service metadata. This ensures downstream Layer 2 (enrichment) can perform 1:1 database lookups for every CVE. Teammates should confirm if downstream consumers prefer this 1:1 record-per-CVE model or a nested `cve_ids: List[str]` list (current schema requires `cve_id: str`).

---

### 7. What still needs to happen before this layer is demo-ready
- Integration with Layer 2 (CVE database enrichment): passing `List[ParsedVulnerability]` directly to Beta's `enrich_vulnerabilities` function once Layer 2's SQLite/PostgreSQL seed table is ready.
