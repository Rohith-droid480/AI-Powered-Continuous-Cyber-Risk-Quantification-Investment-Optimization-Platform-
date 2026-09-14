import io
import time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.enrichment.seed_cves import seed_database
from app.enrichment.db import init_db

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "sample-data"
client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_local_database():
    """Ensures local database is seeded with CVE records before running integration tests."""
    init_db()
    seed_database()


def test_layer1_layer2_end_to_end_integration():
    """
    End-to-End Type A Correctness Test for Layer 1 & Layer 2 Integration:
    1. POST sample-data/enterprise_perimeter_scan.nessus to /scan/upload.
    2. Verify immediate receipt of job_id and status.
    3. Poll GET /scan/{job_id}/status until status is PARSED.
    4. Fetch GET /scan/{job_id}/vulnerabilities (List[EnrichedVulnerability]).
    5. Extract record with cve_id == 'CVE-2021-44228'.
    6. Assert exact match with Layer 2 seeded metrics:
       - enrichment_status == 'FULL'
       - cvss_score == 10.0
       - epss_score == 0.97
       - is_kev == True
    """
    scan_file = SAMPLE_DATA_DIR / "enterprise_perimeter_scan.nessus"
    assert scan_file.exists(), f"Sample scan file not found: {scan_file}"

    with open(scan_file, "rb") as f:
        file_bytes = f.read()

    # Step 1: Upload Nessus scan
    response = client.post(
        "/scan/upload",
        files={"file": ("enterprise_perimeter_scan.nessus", io.BytesIO(file_bytes), "application/xml")},
    )
    assert response.status_code == 200, f"Upload failed: {response.text}"
    upload_data = response.json()
    assert "job_id" in upload_data
    job_id = upload_data["job_id"]

    # Step 2: Poll status until PARSED (in TestClient, background task completes before return, but poll pattern is verified)
    max_attempts = 10
    final_status = None
    for _ in range(max_attempts):
        status_resp = client.get(f"/scan/{job_id}/status")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        if status_data["status"] == "PARSED":
            final_status = "PARSED"
            break
        elif status_data["status"] == "INGESTION_FAILED":
            pytest.fail(f"Job failed unexpectedly: {status_data.get('message')}")
        time.sleep(0.05)

    assert final_status == "PARSED", f"Job did not reach PARSED status: {status_data}"

    # Step 3: Fetch enriched vulnerabilities
    vulns_resp = client.get(f"/scan/{job_id}/vulnerabilities")
    assert vulns_resp.status_code == 200, f"Failed fetching vulnerabilities: {vulns_resp.text}"
    vulns_list = vulns_resp.json()
    assert isinstance(vulns_list, list)
    assert len(vulns_list) == 5, f"Expected 5 findings, got {len(vulns_list)}"

    # Step 4: Extract CVE-2021-44228 (Log4Shell)
    log4j_findings = [v for v in vulns_list if v["cve_id"] == "CVE-2021-44228"]
    assert len(log4j_findings) == 1, "Expected exactly 1 finding for CVE-2021-44228"
    log4j_record = log4j_findings[0]

    # Step 5: Assert enrichment fields match Layer 2 seeded data exactly
    assert log4j_record["enrichment_status"] == "FULL"
    assert log4j_record["cvss_score"] == 10.0
    assert log4j_record["epss_score"] == 0.97
    assert log4j_record["is_kev"] is True

    # Check host/network context preserved from Layer 1
    assert log4j_record["host"] == "192.168.1.10"
    assert log4j_record["port"] == 443
    assert log4j_record["protocol"] == "tcp"
    assert log4j_record["plugin_id"] == "156014"


def test_layer1_layer2_additional_cves_and_failsoft():
    """
    Verifies additional seeded CVEs and fail-soft behavior in the integrated pipeline:
    - CVE-2021-41773: FULL, cvss=7.5, epss=0.8, is_kev=True
    - Corrupted scan: transitions to INGESTION_FAILED cleanly without server crash.
    """
    scan_file = SAMPLE_DATA_DIR / "enterprise_perimeter_scan.nessus"
    with open(scan_file, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/scan/upload",
        files={"file": ("enterprise_perimeter_scan.nessus", io.BytesIO(file_bytes), "application/xml")},
    )
    job_id = response.json()["job_id"]

    vulns_resp = client.get(f"/scan/{job_id}/vulnerabilities")
    vulns_list = vulns_resp.json()

    cve_41773 = next((v for v in vulns_list if v["cve_id"] == "CVE-2021-41773"), None)
    assert cve_41773 is not None
    assert cve_41773["enrichment_status"] == "FULL"
    assert cve_41773["cvss_score"] == 7.5
    assert cve_41773["epss_score"] == 0.80
    assert cve_41773["is_kev"] is True

    # Test malformed scan fail-soft through the pipeline
    malformed_file = SAMPLE_DATA_DIR / "malformed_corrupt.nessus"
    with open(malformed_file, "rb") as f:
        malformed_bytes = f.read()

    malformed_resp = client.post(
        "/scan/upload",
        files={"file": ("malformed_corrupt.nessus", io.BytesIO(malformed_bytes), "application/xml")},
    )
    bad_job_id = malformed_resp.json()["job_id"]
    status_resp = client.get(f"/scan/{bad_job_id}/status")
    assert status_resp.json()["status"] == "INGESTION_FAILED"
    vulns_bad_resp = client.get(f"/scan/{bad_job_id}/vulnerabilities")
    assert vulns_bad_resp.json() == []
