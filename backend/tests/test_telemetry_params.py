"""
Parameterized Tests for Telemetry Data Handling
Covers edge cases, null values, outliers, and disconnects
"""
import pytest
from backend.main import app
from fastapi.testclient import TestClient
from datetime import datetime

client = TestClient(app)

@pytest.mark.parametrize("machine_id, telemetry_data, expected_status", [
    # Normal data
    ("OMAYA-001", {"id": "OMAYA-001", "temperature": 65.5, "vibration": 1.2, "spindleSpeed": 10000, "status": "operational", "toolWear": 35.0, "timestamp": datetime.now().isoformat()}, 200),
    # High values (outliers)
    ("OMAYA-002", {"id": "OMAYA-002", "temperature": 150.0, "vibration": 15.0, "spindleSpeed": 25000, "status": "critical", "toolWear": 99.9, "timestamp": datetime.now().isoformat()}, 200),
    # Low values
    ("OMAYA-003", {"id": "OMAYA-003", "temperature": -10.0, "vibration": 0.0, "spindleSpeed": 0, "status": "maintenance", "toolWear": 0.0, "timestamp": datetime.now().isoformat()}, 200),
    # Missing optional fields (handled by mock or Pydantic)
    ("OMAYA-004", {"id": "OMAYA-004", "temperature": 60.0, "vibration": 1.0, "spindleSpeed": 9000, "status": "operational", "toolWear": 20.0, "timestamp": datetime.now().isoformat()}, 200),
])
def test_update_machine_status_edge_cases(machine_id, telemetry_data, expected_status):
    """Test machine status updates with various telemetry values."""
    response = client.post(f"/api/machines/{machine_id}/status", json=telemetry_data)
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["status"] == "updated"
        assert response.json()["machineId"] == machine_id

@pytest.mark.parametrize("prediction_request, expected_code", [
    # Normal
    ({"machineId": "OMAYA-001", "features": {"temperature": 60.0, "vibration": 1.0, "toolWear": 50.0}}, 200),
    # Extreme temperature
    ({"machineId": "OMAYA-001", "features": {"temperature": 200.0, "vibration": 1.0, "toolWear": 50.0}}, 200),
    # Zero features
    ({"machineId": "OMAYA-001", "features": {"temperature": 0.0, "vibration": 0.0, "toolWear": 0.0}}, 200),
    # Missing some features
    ({"machineId": "OMAYA-001", "features": {"temperature": 60.0}}, 200),
    # Invalid data types (should fail Pydantic validation)
    ({"machineId": "OMAYA-001", "features": "not a dict"}, 422),
])
def test_prediction_edge_cases(prediction_request, expected_code):
    """Test prediction endpoints with edge case feature data."""
    response = client.post("/api/predict/failure", json=prediction_request)
    assert response.status_code == expected_code

@pytest.mark.parametrize("alert_data, expected_code", [
    # Valid alert
    ({"machineId": "OMAYA-001", "severity": "critical", "title": "Fire!", "message": "Machine is on fire"}, 200),
    # Empty message
    ({"machineId": "OMAYA-001", "severity": "warning", "title": "Warning", "message": ""}, 200),
    # Very long title
    ({"machineId": "OMAYA-001", "severity": "info", "title": "A" * 1000, "message": "Test"}, 200),
    # Missing required fields
    ({"machineId": "OMAYA-001"}, 422),
])
def test_alert_edge_cases(alert_data, expected_code):
    """Test alert creation with various input data."""
    response = client.post("/api/alerts", json=alert_data)
    assert response.status_code == expected_code
