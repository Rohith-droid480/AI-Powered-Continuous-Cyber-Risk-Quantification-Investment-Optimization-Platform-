# Milestone Report: Layer 2 — Vulnerability Enrichment & Database Lookup

**Date/time completed:** 2026-09-13T23:10:00+05:30  
**Built by:** Beta (Layer 1 & 2 Owner)  
**Branch/commit:** `layer2-enrichment` (`8307aa6`)  

---

### 1. What was built (plain language, 3–5 sentences)
Layer 2 implements the vulnerability enrichment subsystem that takes parsed vulnerability records from Layer 1 and enriches them with threat intelligence metrics: CVSS v3/v4 base scores, EPSS exploitability probabilities, and CISA Known Exploited Vulnerabilities (KEV) status. A local PostgreSQL/SQLite database seeder (`seed_cves.py`) populates a `cves` table with baseline metrics matching sample scan data without making live external API calls to NVD, EPSS, or CISA. The lookup module (`enrichment.py`) maps each `ParsedVulnerability` to an `EnrichedVulnerability` conforming to the project schema contract. When a CVE is not found in the local database, it enforces a strict fail-soft fallback rule returning baseline metrics (`cvss=0.0`, `epss=0.001`, `is_kev=False`) marked with `enrichment_status=PARTIAL`.

---

### 2. Inputs and outputs (exact schema)

#### Input Schema (`ParsedVulnerability` from `app/schemas/models.py`)
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

#### Output Schema (`EnrichedVulnerability` from `app/schemas/models.py`)
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

#### Database Schema (`cves` table via SQLAlchemy in `app/enrichment/db.py`)
```python
class CVETable(Base):
    __tablename__ = "cves"
    cve_id = Column(String(50), primary_key=True, index=True, nullable=False)
    cvss_score = Column(Float, nullable=False, default=0.0)
    epss_score = Column(Float, nullable=False, default=0.001)
    is_kev = Column(Boolean, nullable=False, default=False)
    description = Column(Text, nullable=True)
```

#### Fallback Rules
- **Known CVE in local DB:** Returns `EnrichmentStatus.FULL`, database `cvss_score`, database `epss_score`, and database `is_kev`.
- **Unknown/Missing CVE:** Returns `EnrichmentStatus.PARTIAL`, `cvss_score=0.0`, `epss_score=0.001`, and `is_kev=False`. Zero network calls, zero exceptions raised.

---

### 3. Tests run and actual results (numerical verification)

Automated tests in `app/tests/test_enrichment.py`: **5 passed in 0.99s** (Full test suite: **20 passed in 1.38s**).

1. **Test 1: Known CVE Hand-Computed Verification (`test_enrich_known_cve_hand_computed`)**:
   - **Input**: `CVE-2021-44228` (Log4Shell), `plugin_id="156014"`, `host="192.168.1.10"`, `port=443`
   - **Expected**: `enrichment_status=EnrichmentStatus.FULL`, `cvss_score=10.0`, `epss_score=0.97`, `is_kev=True`
   - **Actual result**: `enrichment_status=FULL`, `cvss_score=10.0`, `epss_score=0.97`, `is_kev=True` ✓

2. **Test 2: Unknown CVE Strict Fallback (`test_enrich_unknown_cve_strict_fallback`)**:
   - **Input**: `CVE-9999-0000`, `plugin_id="999999"`, `host="10.0.0.99"`, `port=8080`
   - **Expected**: `enrichment_status=EnrichmentStatus.PARTIAL`, `cvss_score=0.0`, `epss_score=0.001`, `is_kev=False`
   - **Actual result**: `enrichment_status=PARTIAL`, `cvss_score=0.0`, `epss_score=0.001`, `is_kev=False` ✓

3. **Test 3: Additional Sample CVEs Matching Layer 1 Data (`test_enrich_additional_sample_cves`)**:
   - **Input A**: `CVE-2021-41773` (Apache Path Traversal) → Expected `cvss=7.5`, `epss=0.80`, `is_kev=True`, `status=FULL` → Got `cvss=7.5`, `epss=0.80`, `is_kev=True`, `status=FULL` ✓
   - **Input B**: `CVE-2023-38606` (Apple WebKit) → Expected `cvss=7.8`, `epss=0.10`, `is_kev=False`, `status=FULL` → Got `cvss=7.8`, `epss=0.10`, `is_kev=False`, `status=FULL` ✓

4. **Test 4: Batch Enrichment (`test_batch_enrichment`)**:
   - **Input**: List of 2 vulnerabilities (`CVE-2021-44228` and `CVE-UNKNOWN-1234`).
   - **Actual result**: Length 2; first record enriched `FULL` (`10.0`, `0.97`, `True`); second record fallback `PARTIAL` (`0.0`, `0.001`, `False`) ✓

5. **Test 5: Database Seeder Idempotency (`test_seed_database_idempotency`)**:
   - **Input**: Calling `seed_database()` sequentially twice.
   - **Actual result**: Second call returns identical record count (6 records) without primary key collisions or duplicate rows ✓

---

### 3.5. How to test this yourself, manually

1. Open PowerShell terminal in `d:\SIH`.
2. Run the seed script:
   ```powershell
   & "C:\Users\Dilip Shekar K\anaconda3\python.exe" -m app.enrichment.seed_cves
   ```
   **Expected working output**:
   ```
   Successfully seeded 6 CVE records into the local database.
   Database seeding completed. 6 CVE records available in local store.
   ```
3. Run the Layer 2 unit tests:
   ```powershell
   & "C:\Users\Dilip Shekar K\anaconda3\python.exe" -m pytest app/tests/test_enrichment.py -v
   ```
   **Expected working output**:
   ```
   5 passed in 0.99s
   ```
4. **Broken result indicators**:
   - Any test failure showing status `PARTIAL` for `CVE-2021-44228`, or non-zero CVSS for an unknown CVE.
   - Network timeouts (which would indicate an unauthorized external API call).

---

### 4. Deviations from PLAYBOOK.md / locked architecture (if any)
None — matches spec exactly.

---

### 5. Claims made in this layer that use words like "verified," "official," or "standard"
- **"CVSS v3.1 / v4.0 base score"**: Numerical base scores stored locally representing standard CVSS severity. Source: First.org CVSS specification.
- **"EPSS exploit prediction probability"**: Exploit Prediction Scoring System probability scores (0.0 to 1.0). Source: First.org EPSS model.
- **"CISA KEV"**: Known Exploited Vulnerabilities catalog flag indicating active in-the-wild exploitation. Source: CISA KEV catalog.
- All lookups are strictly local; no claims of real-time live synchronization are made for this offline hackathon build.

---

### 6. Open questions / methodological uncertainty
- **Fallback EPSS score**: Unrecognized CVEs default to `epss_score=0.001` (0.1% baseline probability). This represents the floor exploitability for novel/unscored vulnerabilities in Layer 3 calibration.
- **Database Engine Support**: Supported via SQLAlchemy for PostgreSQL (with `psycopg2-binary`) and local SQLite fallback (`sqlite:///./cves.db`) to enable resilient offline execution without external database container dependencies.

---

### 7. What still needs to happen before this layer is demo-ready
1. End-to-end wiring with Layer 1's scan upload output (`ParsedVulnerability` list from Nessus parser fed into `enrich_vulnerabilities`).
2. Feeding `EnrichedVulnerability` objects into Layer 3's `calibrate_vulnerability_risk` to produce `CalibratedRiskRecord`.
