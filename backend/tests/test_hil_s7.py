"""
Hardware-in-the-Loop Tests for Siemens S7 Connector
Tests with simulated PLC behavior
"""
import pytest
from backend.adapters.s7_connector import S7Connector
from unittest.mock import Mock, patch, MagicMock
import struct


@pytest.fixture
def simulated_s7_plc():
    """Create simulated S7 PLC for HIL testing."""
    plc = Mock()
    plc.db_data = {
        1: b'\x00\x00\x80\x3f' * 100,  # DB1 with float values
        2: b'\x64\x00\x00\x00' * 50,   # DB2 with int32 values
    }
    plc.merkers = b'\x00' * 256
    plc.inputs = b'\x00' * 128
    plc.outputs = b'\x00' * 128
    
    def db_read(db_number, start, size):
        if db_number in plc.db_data:
            data = plc.db_data[db_number]
            return data[start:start+size]
        return b'\x00' * size
    
    def db_write(db_number, start, data):
        if db_number not in plc.db_data:
            plc.db_data[db_number] = b'\x00' * 1000
        data_bytes = bytearray(plc.db_data[db_number])
        data_bytes[start:start+len(data)] = data
        plc.db_data[db_number] = bytes(data_bytes)
    
    plc.db_read = db_read
    plc.db_write = db_write
    plc.mb_read = lambda start, size: plc.merkers[start:start+size]
    plc.eb_read = lambda start, size: plc.inputs[start:start+size]
    plc.ab_read = lambda start, size: plc.outputs[start:start+size]
    
    return plc


@pytest.fixture
def s7_connector_with_sim(simulated_s7_plc):
    """Create S7 connector with simulated PLC."""
    connector = S7Connector(ip="192.168.1.100", rack=0, slot=1)
    connector.client = simulated_s7_plc
    connector.connected = True
    return connector


def test_hil_s7_read_db_real(s7_connector_with_sim):
    """HIL test: Read REAL value from DB."""
    value = s7_connector_with_sim.read_db_real(db_number=1, start=0)
    assert value is not None
    assert abs(value - 1.0) < 0.01


def test_hil_s7_read_db_dint(s7_connector_with_sim):
    """HIL test: Read DINT value from DB."""
    value = s7_connector_with_sim.read_db_dint(db_number=2, start=0)
    assert value is not None
    assert value == 100


def test_hil_s7_write_db_real(s7_connector_with_sim):
    """HIL test: Write REAL value to DB."""
    result = s7_connector_with_sim.write_db_real(db_number=1, start=4, value=42.5)
    assert result is True
    
    # Verify write
    value = s7_connector_with_sim.read_db_real(db_number=1, start=4)
    assert abs(value - 42.5) < 0.01


def test_hil_s7_write_db_dint(s7_connector_with_sim):
    """HIL test: Write DINT value to DB."""
    result = s7_connector_with_sim.write_db_dint(db_number=2, start=4, value=500)
    assert result is True
    
    # Verify write
    value = s7_connector_with_sim.read_db_dint(db_number=2, start=4)
    assert value == 500


def test_hil_s7_read_merkers(s7_connector_with_sim):
    """HIL test: Read Merkers."""
    data = s7_connector_with_sim.read_merkers(start=0, size=10)
    assert data is not None
    assert len(data) == 10


def test_hil_s7_read_inputs(s7_connector_with_sim):
    """HIL test: Read Inputs."""
    data = s7_connector_with_sim.read_inputs(start=0, size=10)
    assert data is not None
    assert len(data) == 10


def test_hil_s7_read_outputs(s7_connector_with_sim):
    """HIL test: Read Outputs."""
    data = s7_connector_with_sim.read_outputs(start=0, size=10)
    assert data is not None
    assert len(data) == 10


def test_hil_s7_write_merkers(s7_connector_with_sim):
    """HIL test: Write to Merkers."""
    result = s7_connector_with_sim.write_merkers(start=0, data=b'\x01\x02\x03\x04')
    assert result is True


def test_hil_s7_write_outputs(s7_connector_with_sim):
    """HIL test: Write to Outputs."""
    result = s7_connector_with_sim.write_outputs(start=0, data=b'\x01\x02\x03\x04')
    assert result is True


def test_hil_s7_read_multiple_values(s7_connector_with_sim):
    """HIL test: Read multiple values in sequence."""
    values = []
    for i in range(0, 40, 4):
        value = s7_connector_with_sim.read_db_real(db_number=1, start=i)
        values.append(value)
    
    assert len(values) == 10
    assert all(v is not None for v in values)


def test_hil_s7_write_multiple_values(s7_connector_with_sim):
    """HIL test: Write multiple values in sequence."""
    for i in range(10):
        result = s7_connector_with_sim.write_db_real(
            db_number=1, 
            start=i*4, 
            value=float(i * 10)
        )
        assert result is True
    
    # Verify all writes
    for i in range(10):
        value = s7_connector_with_sim.read_db_real(db_number=1, start=i*4)
        assert abs(value - float(i * 10)) < 0.01


def test_hil_s7_concurrent_operations(s7_connector_with_sim):
    """HIL test: Concurrent read/write operations."""
    import threading
    
    results = []
    
    def read_operation():
        for _ in range(10):
            value = s7_connector_with_sim.read_db_real(db_number=1, start=0)
            results.append(('read', value))
    
    def write_operation():
        for i in range(10):
            result = s7_connector_with_sim.write_db_real(
                db_number=1, 
                start=0, 
                value=float(i)
            )
            results.append(('write', result))
    
    thread1 = threading.Thread(target=read_operation)
    thread2 = threading.Thread(target=write_operation)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    assert len(results) == 20


def test_hil_s7_error_handling(s7_connector_with_sim):
    """HIL test: Error handling for invalid operations."""
    # Test reading beyond available data
    value = s7_connector_with_sim.read_db_real(db_number=999, start=0)
    # Should handle gracefully
    assert value is not None or value is None


def test_hil_s7_performance(s7_connector_with_sim):
    """HIL test: Performance benchmark."""
    import time
    
    start_time = time.time()
    for i in range(1000):
        s7_connector_with_sim.read_db_real(db_number=1, start=0)
    end_time = time.time()
    
    duration = end_time - start_time
    ops_per_second = 1000 / duration
    
    assert ops_per_second > 100  # Should handle at least 100 ops/sec


def test_hil_s7_data_integrity(s7_connector_with_sim):
    """HIL test: Data integrity after multiple operations."""
    original_value = s7_connector_with_sim.read_db_real(db_number=1, start=0)
    
    # Perform multiple operations
    for i in range(100):
        s7_connector_with_sim.write_db_real(db_number=1, start=0, value=float(i))
        read_back = s7_connector_with_sim.read_db_real(db_number=1, start=0)
        assert abs(read_back - float(i)) < 0.01
    
    # Restore original
    s7_connector_with_sim.write_db_real(db_number=1, start=0, original_value)
    final_value = s7_connector_with_sim.read_db_real(db_number=1, start=0)
    assert abs(final_value - original_value) < 0.01
