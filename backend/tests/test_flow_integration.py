import pytest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime

# Import modules to test
from kafka_streams import process_telemetry_event, telemetry_aggregator
from websocket_manager import ConnectionManager
from redis_cache import RedisCache

@pytest.fixture
def mock_ws():
    return MagicMock()

@pytest.mark.asyncio
async def test_telemetry_to_aggregator_flow():
    # 1. Simulate a telemetry event coming from Kafka
    machine_id = "OMAYA-FLOW-001"
    event = {
        "machine_id": machine_id,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "temperature": 72.5,
            "vibration": 1.8,
            "spindleSpeed": 11000
        },
        "event_type": "telemetry"
    }

    # 2. Process the event
    process_telemetry_event(event)

    # 3. Verify it reached the aggregator
    metrics = telemetry_aggregator.get_metrics(machine_id)
    assert metrics["temperature"]["avg"] == 72.5
    assert metrics["sample_count"] >= 1

@patch("redis_cache.redis.Redis")
def test_cache_integration(mock_redis_cls):
    # Setup mock redis
    mock_redis = mock_redis_cls.return_value
    mock_redis.get.return_value = json.dumps({"status": "ok"})

    cache = RedisCache()
    cache.client = mock_redis

    # Test set/get flow
    cache.set("test_key", {"data": 123})
    mock_redis.setex.assert_called()

    val = cache.get("test_key")
    assert val["status"] == "ok"
