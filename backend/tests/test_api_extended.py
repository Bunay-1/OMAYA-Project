import pytest
from fastapi.testclient import TestClient
from main import app
import json
from datetime import datetime

@pytest.fixture
def client():
    return TestClient(app)

def test_root_extended(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "status" in data
    assert data["status"] == "operational"

def test_health_extended(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_self_test_extended(client):
    response = client.get("/api/self-test")
    assert response.status_code == 200
    data = response.json()
    assert "tests" in data
    # Check if all keys exist in tests dict
    expected_tests = ["api", "websocket", "redis", "ai_models", "kafka", "data_lake", "database"]
    for test in expected_tests:
        assert test in data["tests"]

def test_get_machines_pagination_mock(client):
    # Testing our mock implementation handles large count
    response = client.get("/api/machines")
    assert response.status_code == 200
    data = response.json()
    assert len(data["machines"]) == 120
    assert data["count"] == 120

def test_get_machine_not_found_extended(client):
    # Our current mock returns a machine for ANY ID
    response = client.get("/api/machines/NONEXISTENT-999")
    assert response.status_code == 200
    assert response.json()["id"] == "NONEXISTENT-999"

def test_update_machine_status_validation(client):
    # Missing required fields
    invalid_data = {"id": "OMAYA-001", "status": "operational"}
    response = client.post("/api/machines/OMAYA-001/status", json=invalid_data)
    assert response.status_code == 422 # Pydantic validation error

def test_create_alert_extended(client):
    alert_data = {
        "machineId": "OMAYA-001",
        "severity": "critical",
        "title": "Extended Test Alert",
        "message": "Testing alert creation deeply"
    }
    response = client.post("/api/alerts", json=alert_data)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "critical"
    assert "id" in data
    assert "timestamp" in data

def test_simulate_scenarios(client):
    scenarios = ["machine_failure", "high_wear", "temperature_spike", "unknown"]
    for scenario in scenarios:
        response = client.post("/api/simulate", json={"type": scenario, "machineId": "OMAYA-001"})
        assert response.status_code == 200
        assert response.json()["status"] == "simulated"

def test_predict_failure_missing_features(client):
    pred_data = {
        "machineId": "OMAYA-001",
        "features": {} # Empty features should use defaults
    }
    response = client.post("/api/predict/failure", json=pred_data)
    assert response.status_code == 200
    assert "failureProbability" in response.json()

def test_predict_rul_extended(client):
    pred_data = {
        "machineId": "OMAYA-001",
        "features": {"temperature": 90, "vibration": 4.5}
    }
    response = client.post("/api/predict/rul", json=pred_data)
    assert response.status_code == 200
    data = response.json()
    assert data["rul_hours"] < 100 # High stress should lead to low RUL

def test_analytics_endpoints(client):
    endpoints = [
        "/api/analytics/telemetry/OMAYA-001",
        "/api/analytics/alerts/OMAYA-001",
        "/api/analytics/critical-alerts",
        "/api/analytics/summary"
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200

def test_drift_status_extended(client):
    response = client.get("/api/drift/status")
    assert response.status_code == 200
    assert "hasDrift" in response.json()

def test_data_lake_stats_extended(client):
    response = client.get("/api/data-lake/stats")
    assert response.status_code == 200

def test_audit_logs_extended(client):
    response = client.get("/api/audit/recent?limit=10")
    assert response.status_code == 200
    assert "events" in response.json()

def test_multi_region_status_extended(client):
    response = client.get("/api/multi-region/status")
    assert response.status_code == 200

def test_secrets_status_extended(client):
    response = client.get("/api/secrets/status")
    assert response.status_code == 200

def test_explainability_extended(client):
    response = client.get("/api/explainability/OMAYA-001")
    assert response.status_code == 200
    data = response.json()
    assert "shap" in data
    assert "lime" in data
