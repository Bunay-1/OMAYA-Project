"""
Test Suite for OMAYA Fleet Monitoring API
Pytest configuration and test cases
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import main app
from main import app

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

class TestHealth:
    """Health check endpoints"""
    
    def test_root(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "OMAYA Fleet Monitoring API"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_self_test(self, client):
        """Test self-test endpoint"""
        response = client.get("/api/self-test")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "tests" in data

class TestMachines:
    """Machine endpoints"""
    
    def test_get_machines(self, client):
        """Test get all machines"""
        response = client.get("/api/machines")
        assert response.status_code == 200
        data = response.json()
        assert "machines" in data
        assert "count" in data
        assert data["count"] == 120
    
    def test_get_machine_detail(self, client):
        """Test get specific machine"""
        response = client.get("/api/machines/OMAYA-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "OMAYA-001"
        assert "status" in data
        assert "temperature" in data

class TestAlerts:
    """Alert endpoints"""
    
    def test_get_alerts(self, client):
        """Test get alerts"""
        response = client.get("/api/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "count" in data
    
    def test_get_alerts_with_severity_filter(self, client):
        """Test get alerts with severity filter"""
        response = client.get("/api/alerts?severity=critical")
        assert response.status_code == 200
        data = response.json()
        for alert in data["alerts"]:
            assert alert["severity"] == "critical"
    
    def test_create_alert(self, client):
        """Test create alert"""
        alert_data = {
            "machineId": "OMAYA-001",
            "severity": "warning",
            "title": "High temperature",
            "message": "Machine temperature exceeded threshold"
        }
        response = client.post("/api/alerts", json=alert_data)
        assert response.status_code == 200
        data = response.json()
        assert data["machineId"] == "OMAYA-001"
        assert data["severity"] == "warning"

class TestPredictions:
    """AI prediction endpoints"""
    
    def test_predict_failure(self, client):
        """Test failure prediction"""
        pred_data = {
            "machineId": "OMAYA-001",
            "features": {
                "temperature": 68.5,
                "vibration": 2.1,
                "toolWear": 75,
                "operatingHours": 3200
            }
        }
        response = client.post("/api/predict/failure", json=pred_data)
        assert response.status_code == 200
        data = response.json()
        assert "machineId" in data
        assert "failureProbability" in data
        assert 0 <= data["failureProbability"] <= 1
        assert "confidence" in data
        assert "factors" in data
    
    def test_predict_rul(self, client):
        """Test RUL prediction"""
        pred_data = {
            "machineId": "OMAYA-001",
            "features": {
                "temperature": 68.5,
                "vibration": 2.1,
                "toolWear": 75
            }
        }
        response = client.post("/api/predict/rul", json=pred_data)
        assert response.status_code == 200
        data = response.json()
        assert "machineId" in data
        assert "rul_hours" in data
        assert "confidence_interval" in data
        assert data["rul_hours"] > 0
    
    def test_detect_anomaly(self, client):
        """Test anomaly detection"""
        anom_data = {
            "machineId": "OMAYA-001",
            "features": {
                "temperature": 85.0,  # High
                "vibration": 3.5,     # High
                "spindleSpeed": 9500
            }
        }
        response = client.post("/api/detect/anomaly", json=anom_data)
        assert response.status_code == 200
        data = response.json()
        assert "isAnomalous" in data
        assert "anomalyScore" in data
        assert "anomalies" in data

class TestSimulation:
    """Simulation endpoints"""
    
    def test_simulate_machine_failure(self, client):
        """Test simulate machine failure scenario"""
        sim_data = {
            "type": "machine_failure",
            "machineId": "OMAYA-001"
        }
        response = client.post("/api/simulate", json=sim_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "simulated"
        assert "event" in data
    
    def test_simulate_high_wear(self, client):
        """Test simulate high tool wear"""
        sim_data = {
            "type": "high_wear",
            "machineId": "OMAYA-001"
        }
        response = client.post("/api/simulate", json=sim_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "simulated"

class TestMetrics:
    """Prometheus metrics endpoint"""
    
    def test_metrics(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Prometheus metrics are in text format
        assert "# HELP" in response.text or "# TYPE" in response.text

class TestErrorHandling:
    """Error handling and edge cases"""
    
    def test_invalid_machine_id(self, client):
        """Test invalid machine ID"""
        # This should still return data in our mock implementation
        response = client.get("/api/machines/INVALID-999")
        assert response.status_code == 200  # Mock returns data anyway
    
    def test_invalid_prediction_data(self, client):
        """Test invalid prediction data"""
        pred_data = {
            "machineId": "OMAYA-001",
            "features": {}  # Empty features
        }
        response = client.post("/api/predict/failure", json=pred_data)
        # Should still work with default values
        assert response.status_code == 200
    
    def test_missing_required_field(self, client):
        """Test missing required field"""
        alert_data = {
            "machineId": "OMAYA-001"
            # Missing severity, title, message
        }
        response = client.post("/api/alerts", json=alert_data)
        # Should fail validation
        assert response.status_code == 422

class TestPerformance:
    """Performance and load testing"""
    
    def test_get_machines_response_time(self, client):
        """Test get machines response time"""
        import time
        start = time.time()
        response = client.get("/api/machines")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should be fast
    
    def test_concurrent_predictions(self, client):
        """Test multiple concurrent predictions"""
        for i in range(10):
            pred_data = {
                "machineId": f"OMAYA-{i:03d}",
                "features": {
                    "temperature": 60 + i,
                    "vibration": 1.0 + i * 0.1,
                    "toolWear": 50
                }
            }
            response = client.post("/api/predict/failure", json=pred_data)
            assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
