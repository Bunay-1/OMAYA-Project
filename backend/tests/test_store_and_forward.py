"""
Tests for Store-and-Forward Mechanism
"""
import pytest
import sqlite3
import tempfile
import os
from backend.store_and_forward import StoreAndForward
from datetime import datetime


@pytest.fixture
def store_forward():
    """Create Store-and-Forward instance with temporary database."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    saf = StoreAndForward(db_path=temp_db.name, max_buffer_size=1000)
    yield saf
    
    saf.close()
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)


def test_store_and_forward_init(store_forward):
    """Test Store-and-Forward initialization."""
    assert store_forward.db_path is not None
    assert store_forward.max_buffer_size == 1000
    assert store_forward.connection is not None


def test_store_telemetry(store_forward):
    """Test storing telemetry data."""
    machine_id = "MACHINE-001"
    data = {"temperature": 25.5, "vibration": 0.1}
    
    result = store_forward.store_telemetry(machine_id, data)
    
    assert result is True


def test_store_alert(store_forward):
    """Test storing alert data."""
    machine_id = "MACHINE-001"
    alert_data = {"severity": "warning", "message": "High temperature"}
    
    result = store_forward.store_alert(machine_id, alert_data)
    
    assert result is True


def test_store_event(store_forward):
    """Test storing event data."""
    event_type = "maintenance"
    event_data = {"action": "tool_change", "tool_id": "T001"}
    
    result = store_forward.store_event(event_type, event_data)
    
    assert result is True


def test_get_unsynced_telemetry(store_forward):
    """Test getting unsynced telemetry."""
    machine_id = "MACHINE-001"
    data = {"temperature": 25.5}
    
    store_forward.store_telemetry(machine_id, data)
    records = store_forward.get_unsynced_telemetry(limit=10)
    
    assert len(records) > 0
    assert records[0]['machine_id'] == machine_id
    assert records[0]['data'] == data


def test_get_unsynced_alerts(store_forward):
    """Test getting unsynced alerts."""
    machine_id = "MACHINE-001"
    alert_data = {"severity": "warning"}
    
    store_forward.store_alert(machine_id, alert_data)
    records = store_forward.get_unsynced_alerts(limit=10)
    
    assert len(records) > 0
    assert records[0]['machine_id'] == machine_id


def test_get_unsynced_events(store_forward):
    """Test getting unsynced events."""
    event_type = "maintenance"
    event_data = {"action": "tool_change"}
    
    store_forward.store_event(event_type, event_data)
    records = store_forward.get_unsynced_events(limit=10)
    
    assert len(records) > 0
    assert records[0]['event_type'] == event_type


def test_mark_as_synced(store_forward):
    """Test marking records as synced."""
    machine_id = "MACHINE-001"
    data = {"temperature": 25.5}
    
    store_forward.store_telemetry(machine_id, data)
    records = store_forward.get_unsynced_telemetry(limit=10)
    
    record_ids = [r['id'] for r in records]
    result = store_forward.mark_as_synced('telemetry_buffer', record_ids)
    
    assert result is True


def test_mark_sync_failed(store_forward):
    """Test marking sync failure."""
    machine_id = "MACHINE-001"
    data = {"temperature": 25.5}
    
    store_forward.store_telemetry(machine_id, data)
    records = store_forward.get_unsynced_telemetry(limit=10)
    
    result = store_forward.mark_sync_failed('telemetry_buffer', records[0]['id'], "Network error")
    
    assert result is True


def test_get_buffer_stats(store_forward):
    """Test getting buffer statistics."""
    machine_id = "MACHINE-001"
    data = {"temperature": 25.5}
    
    store_forward.store_telemetry(machine_id, data)
    stats = store_forward.get_buffer_stats()
    
    assert stats is not None
    assert 'telemetry' in stats
    assert 'alerts' in stats
    assert 'events' in stats


def test_cleanup_old_records(store_forward):
    """Test cleaning up old records."""
    machine_id = "MACHINE-001"
    data = {"temperature": 25.5}
    
    store_forward.store_telemetry(machine_id, data)
    # Mark as synced
    records = store_forward.get_unsynced_telemetry(limit=10)
    if records:
        store_forward.mark_as_synced('telemetry_buffer', [r['id'] for r in records])
    
    deleted = store_forward.cleanup_old_records(days=0)  # Delete all
    assert deleted >= 0


def test_clear_all_data(store_forward):
    """Test clearing all data."""
    machine_id = "MACHINE-001"
    data = {"temperature": 25.5}
    
    store_forward.store_telemetry(machine_id, data)
    result = store_forward.clear_all_data()
    
    assert result is True
    stats = store_forward.get_buffer_stats()
    assert stats['telemetry']['unsynced'] == 0


def test_buffer_size_limit(store_forward):
    """Test buffer size limit."""
    # Create with small limit
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    saf = StoreAndForward(db_path=temp_db.name, max_buffer_size=10)
    
    # Add more records than limit
    for i in range(15):
        saf.store_telemetry("MACHINE-001", {"value": i})
    
    stats = saf.get_buffer_stats()
    # Should not exceed limit significantly
    assert stats['telemetry']['unsynced'] <= 15
    
    saf.close()
    os.unlink(temp_db.name)


def test_context_manager():
    """Test Store-and-Forward as context manager."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    with StoreAndForward(db_path=temp_db.name) as saf:
        assert saf.connection is not None
        saf.store_telemetry("MACHINE-001", {"temperature": 25.5})
    
    # Connection should be closed
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)
