import pytest
from unittest.mock import MagicMock, patch
from data_lake import DataLakeClient
import json
from io import BytesIO

@pytest.fixture
def mock_minio():
    with patch('minio.Minio') as mock:
        yield mock

def test_data_lake_init(mock_minio):
    client = DataLakeClient()
    assert client.endpoint == "localhost:9000"
    # minio.Minio() is called inside _connect()

def test_store_telemetry(mock_minio):
    client = DataLakeClient()
    client.connected = True
    client.client = MagicMock()

    data = {"temp": 60}
    res = client.store_telemetry("M1", data)

    assert res is True
    client.client.put_object.assert_called_once()

def test_store_prediction(mock_minio):
    client = DataLakeClient()
    client.connected = True
    client.client = MagicMock()

    prediction = {"prob": 0.5}
    res = client.store_prediction("M1", prediction)

    assert res is True
    client.client.put_object.assert_called_once()

def test_store_alert(mock_minio):
    client = DataLakeClient()
    client.connected = True
    client.client = MagicMock()

    alert = {"id": "A1", "severity": "critical"}
    res = client.store_alert(alert)

    assert res is True
    client.client.put_object.assert_called_once()
