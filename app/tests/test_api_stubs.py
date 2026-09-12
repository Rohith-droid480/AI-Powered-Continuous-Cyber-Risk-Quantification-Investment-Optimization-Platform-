from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scan_upload_stub():
    response = client.post("/scan/upload")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job_stub_001"
    assert data["status"] == "PARSED"


def test_scan_results_stub():
    response = client.get("/scan/job_stub_001/results")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job_stub_001"
    assert data["status"] == "COMPLETED"
    assert "simulation_results" in data
    assert "optimization_results" in data
