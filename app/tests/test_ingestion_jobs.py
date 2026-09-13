import io
from pathlib import Path
from fastapi.testclient import TestClient

from app.api.main import app
from app.ingestion.jobs import JobManager
from app.schemas.models import JobStatusEnum

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "sample-data"
client = TestClient(app)


def test_job_manager_lifecycle_success():
    """
    Unit test for JobManager with hand-computable expected outputs:
    1. Create job -> status is PROCESSING.
    2. Execute process_scan_job on a 1-item XML -> status is PARSED.
    3. Assert parsed_vulnerabilities length is exactly 1 with exact values.
    """
    jm = JobManager()
    jid = jm.create_job()
    job = jm.get_job(jid)
    assert job is not None
    assert job.status == JobStatusEnum.PROCESSING

    valid_xml = b"""<?xml version="1.0" ?>
<NessusClientData_v2>
  <Report name="Test Scan">
    <ReportHost name="10.20.30.40">
      <ReportItem port="80" protocol="tcp" severity="2" pluginID="12345" pluginName="Test Item">
        <description>Sample description.</description>
        <cve>CVE-2023-9999</cve>
      </ReportItem>
    </ReportHost>
  </Report>
</NessusClientData_v2>
"""
    jm.process_scan_job(jid, valid_xml)

    updated_job = jm.get_job(jid)
    assert updated_job.status == JobStatusEnum.PARSED
    assert "Successfully parsed 1 vulnerabilities" in updated_job.message
    assert len(updated_job.parsed_vulnerabilities) == 1
    v = updated_job.parsed_vulnerabilities[0]
    assert v.cve_id == "CVE-2023-9999"
    assert v.plugin_id == "12345"
    assert v.plugin_name == "Test Item"
    assert v.host == "10.20.30.40"
    assert v.port == 80
    assert v.protocol == "tcp"
    assert v.severity == 2
    assert v.description == "Sample description."


def test_job_manager_fail_soft_malformed_xml():
    """
    Fail-soft test: Verifies JobManager cleanly transitions to INGESTION_FAILED
    when given malformed XML bytes, without throwing uncaught exceptions or crashing.
    """
    jm = JobManager()
    jid = jm.create_job()
    corrupted_xml = b"<<<THIS IS NOT XML>>>"

    jm.process_scan_job(jid, corrupted_xml)

    failed_job = jm.get_job(jid)
    assert failed_job.status == JobStatusEnum.INGESTION_FAILED
    assert "Ingestion failed" in failed_job.message
    assert len(failed_job.parsed_vulnerabilities) == 0


def test_api_upload_valid_enterprise_scan():
    """
    Integration test for POST /scan/upload -> GET /scan/{job_id}/status -> GET /scan/{job_id}/vulnerabilities.
    Hand-computable expected count: 5 vulnerabilities.
    """
    scan_path = SAMPLE_DATA_DIR / "enterprise_perimeter_scan.nessus"
    with open(scan_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/scan/upload",
        files={"file": ("enterprise_perimeter_scan.nessus", io.BytesIO(file_bytes), "application/xml")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    job_id = data["job_id"]
    assert job_id.startswith("job_")

    # In TestClient, BackgroundTasks are executed synchronously on endpoint exit
    status_resp = client.get(f"/scan/{job_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["job_id"] == job_id
    assert status_data["status"] == "PARSED"
    assert "Successfully parsed 5 vulnerabilities" in status_data["message"]

    vulns_resp = client.get(f"/scan/{job_id}/vulnerabilities")
    assert vulns_resp.status_code == 200
    vulns_data = vulns_resp.json()
    assert len(vulns_data) == 5

    cves = [v["cve_id"] for v in vulns_data]
    assert "CVE-2021-44228" in cves
    assert "CVE-2020-1472" in cves


def test_api_upload_malformed_scan_triggers_ingestion_failed():
    """
    Fail-soft API test: Verifies POST /scan/upload with a corrupted .nessus file
    triggers the INGESTION_FAILED status cleanly without causing a 500 error or crash.
    """
    malformed_path = SAMPLE_DATA_DIR / "malformed_corrupt.nessus"
    with open(malformed_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/scan/upload",
        files={"file": ("malformed_corrupt.nessus", io.BytesIO(file_bytes), "application/xml")},
    )
    assert response.status_code == 200
    data = response.json()
    job_id = data["job_id"]

    # Check status endpoint
    status_resp = client.get(f"/scan/{job_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["status"] == "INGESTION_FAILED"
    assert "Ingestion failed" in status_data["message"]

    # Check vulnerabilities endpoint for failed job
    vulns_resp = client.get(f"/scan/{job_id}/vulnerabilities")
    assert vulns_resp.status_code == 200
    vulns_data = vulns_resp.json()
    assert vulns_data == []


def test_api_upload_empty_scan_triggers_ingestion_failed():
    """
    Verifies uploading an empty file triggers INGESTION_FAILED cleanly.
    """
    response = client.post(
        "/scan/upload",
        files={"file": ("empty.nessus", io.BytesIO(b""), "application/xml")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "INGESTION_FAILED"
    assert "empty" in data["message"].lower()


def test_api_get_status_not_found():
    """Verifies 404 is returned for an unknown job_id."""
    response = client.get("/scan/non_existent_job_123/status")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
