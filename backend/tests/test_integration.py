"""
Integration Tests for OMAYA Fleet Monitoring
Testing integration with Redis, Kafka, and Data Lake
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from redis_cache import cache
from kafka_producer import producer as kafka_producer
from data_lake import data_lake
from secrets_manager import secrets_manager
import psycopg2

@pytest.fixture
def client():
    return TestClient(app)

class TestRedisIntegration:
    """Tests for Redis cache integration"""

    def test_redis_connection(self):
        """Test if Redis client is initialized"""
        if cache.client:
            try:
                cache.client.ping()
                assert True
            except Exception:
                pytest.skip("Redis server not available")
        else:
            pytest.skip("Redis client not initialized")

    def test_prediction_caching(self, client):
        """Test if predictions are being cached in Redis"""
        pred_data = {
            "machineId": "OMAYA-TEST-001",
            "features": {
                "temperature": 60.0,
                "vibration": 1.0,
                "toolWear": 50
            }
        }

        # First request
        response1 = client.post("/api/predict/failure", json=pred_data)
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request
        response2 = client.post("/api/predict/failure", json=pred_data)
        assert response2.status_code == 200
        data2 = response2.json()

        if cache.client:
            assert data2.get("cached") == True

class TestKafkaIntegration:
    """Tests for Kafka integration"""

    @patch("kafka_producer.MachineEventProducer.publish_telemetry")
    def test_telemetry_published_to_kafka(self, mock_publish, client):
        """Test if telemetry updates are published to Kafka"""
        status_data = {
            "id": "OMAYA-001",
            "status": "operational",
            "temperature": 65.0,
            "vibration": 1.2,
            "spindleSpeed": 10000,
            "toolWear": 45.0,
            "timestamp": "2024-01-01T00:00:00Z"
        }

        response = client.post("/api/machines/OMAYA-001/status", json=status_data)
        assert response.status_code == 200
        mock_publish.assert_called()

class TestDataLakeIntegration:
    """Tests for Data Lake (MinIO) integration"""

    def test_data_lake_connection(self):
        """Test if Data Lake client is connected"""
        if not data_lake.connected:
            pytest.skip("Data Lake (MinIO) not available")
        assert data_lake.client is not None

    @patch("data_lake.DataLakeClient.store_prediction")
    def test_prediction_stored_in_data_lake(self, mock_store, client):
        """Test if predictions are stored in Data Lake"""
        pred_data = {
            "machineId": "OMAYA-STORE-001",
            "features": {
                "temperature": 60.0,
                "vibration": 1.0,
                "toolWear": 50
            }
        }

        response = client.post("/api/predict/failure", json=pred_data)
        assert response.status_code == 200
        mock_store.assert_called()

class TestDatabaseIntegration:
    """Tests for Database (TimescaleDB) integration"""

    def test_database_credentials(self):
        """Test if database credentials can be retrieved"""
        creds = secrets_manager.get_database_credentials()
        assert creds["host"] is not None
        assert creds["database"] == "omaya_monitoring"

    def test_database_connection(self):
        """Test real database connection"""
        creds = secrets_manager.get_database_credentials()
        try:
            conn = psycopg2.connect(
                host=creds["host"],
                port=creds["port"],
                database=creds["database"],
                user=creds["username"],
                password=creds["password"],
                connect_timeout=3
            )
            assert conn is not None
            conn.close()
        except Exception:
            pytest.skip("TimescaleDB not available")

class TestEnterpriseAnalytics:
    """Tests for advanced analytics endpoints"""

    def test_get_telemetry_analytics(self, client):
        response = client.get("/api/analytics/telemetry/OMAYA-001")
        assert response.status_code == 200
        assert "metrics" in response.json()

    def test_get_critical_alerts(self, client):
        response = client.get("/api/analytics/critical-alerts")
        assert response.status_code == 200
        assert "alerts" in response.json()

    def test_get_drift_status(self, client):
        response = client.get("/api/drift/status")
        assert response.status_code == 200
        assert "hasDrift" in response.json()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
