"""
Tests for Siemens S7 Connector
"""
import pytest
from backend.adapters.s7_connector import S7Connector
from unittest.mock import Mock, patch
import struct


@pytest.fixture
def s7_connector():
    """Create S7 connector instance with mocked client."""
    connector = S7Connector(ip="192.168.1.100", rack=0, slot=1)
    connector.client = Mock()
    return connector


def test_s7_connector_init(s7_connector):
    """Test S7 connector initialization."""
    assert s7_connector.ip == "192.168.1.100"
    assert s7_connector.rack == 0
    assert s7_connector.slot == 1
    assert s7_connector.connected is False


def test_s7_connect_success(s7_connector):
    """Test successful connection to S7 PLC."""
    s7_connector.client.connect.return_value = None
    
    result = s7_connector.connect()
    
    assert result is True
    assert s7_connector.connected is True
    s7_connector.client.set_connection_params.assert_called_once_with("192.168.1.100", 0, 1)


def test_s7_connect_failure(s7_connector):
    """Test failed connection to S7 PLC."""
    s7_connector.client.connect.side_effect = Exception("Connection failed")
    
    result = s7_connector.connect()
    
    assert result is False
    assert s7_connector.connected is False
    assert s7_connector.last_error is not None


def test_s7_disconnect(s7_connector):
    """Test disconnection from S7 PLC."""
    s7_connector.connected = True
    
    result = s7_connector.disconnect()
    
    assert result is True
    assert s7_connector.connected is False
    s7_connector.client.disconnect.assert_called_once()


def test_read_db_success(s7_connector):
    """Test reading data block."""
    s7_connector.client.db_read.return_value = b'\x01\x02\x03\x04'
    s7_connector.connected = True
    
    data = s7_connector.read_db(db_number=1, start=0, size=4)
    
    assert data == b'\x01\x02\x03\x04'
    s7_connector.client.db_read.assert_called_once_with(1, 0, 4)


def test_write_db_success(s7_connector):
    """Test writing to data block."""
    s7_connector.connected = True
    
    result = s7_connector.write_db(db_number=1, start=0, data=b'\x01\x02')
    
    assert result is True
    s7_connector.client.db_write.assert_called_once_with(1, 0, b'\x01\x02')


def test_read_db_real(s7_connector):
    """Test reading REAL value from DB."""
    # Big Endian float for 1.0
    s7_connector.client.db_read.return_value = struct.pack('>f', 1.0)
    s7_connector.connected = True
    
    value = s7_connector.read_db_real(db_number=1, start=0)
    
    assert value is not None
    assert abs(value - 1.0) < 0.01


def test_read_db_dint(s7_connector):
    """Test reading DINT value from DB."""
    # Big Endian int32 for 100
    s7_connector.client.db_read.return_value = struct.pack('>i', 100)
    s7_connector.connected = True
    
    value = s7_connector.read_db_dint(db_number=1, start=0)
    
    assert value is not None
    assert value == 100


def test_read_db_bool(s7_connector):
    """Test reading BOOL value from DB."""
    s7_connector.client.db_read.return_value = b'\x01'
    s7_connector.connected = True
    
    value = s7_connector.read_db_bool(db_number=1, start=0, bit=0)
    
    assert value is True


def test_read_merkers(s7_connector):
    """Test reading Merkers."""
    s7_connector.client.mb_read.return_value = b'\x01\x02\x03\x04'
    s7_connector.connected = True
    
    data = s7_connector.read_merkers(start=0, size=4)
    
    assert data == b'\x01\x02\x03\x04'
    s7_connector.client.mb_read.assert_called_once()


def test_read_inputs(s7_connector):
    """Test reading Inputs."""
    s7_connector.client.eb_read.return_value = b'\x01\x02'
    s7_connector.connected = True
    
    data = s7_connector.read_inputs(start=0, size=2)
    
    assert data == b'\x01\x02'
    s7_connector.client.eb_read.assert_called_once()


def test_read_outputs(s7_connector):
    """Test reading Outputs."""
    s7_connector.client.ab_read.return_value = b'\x01\x02'
    s7_connector.connected = True
    
    data = s7_connector.read_outputs(start=0, size=2)
    
    assert data == b'\x01\x02'
    s7_connector.client.ab_read.assert_called_once()


def test_context_manager(s7_connector):
    """Test S7 connector as context manager."""
    # Patch connect and disconnect to avoid real network calls
    with patch.object(S7Connector, 'connect', side_effect=lambda: setattr(s7_connector, 'connected', True) or True):
        with patch.object(S7Connector, 'disconnect', side_effect=lambda: setattr(s7_connector, 'connected', False) or True):
            with s7_connector as connector:
                assert connector.connected is True

            assert connector.connected is False


def test_get_last_error(s7_connector):
    """Test getting last error."""
    s7_connector.last_error = "Test error"
    assert s7_connector.get_last_error() == "Test error"
