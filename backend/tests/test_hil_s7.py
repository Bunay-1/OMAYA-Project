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
    # Snap7 uses Big Endian (Network Byte Order)
    plc.db_data = {
        1: struct.pack('>f', 1.0) * 100,  # DB1 with float values (1.0)
        2: struct.pack('>i', 100) * 50,   # DB2 with int32 values (100)
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
    plc.mb_write = lambda start, data: True
    plc.ab_write = lambda start, data: True
    
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
