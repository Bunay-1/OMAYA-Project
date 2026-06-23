"""
Tests for Siemens S7 Connector
"""
import pytest
from backend.adapters.s7_connector import S7Connector
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def s7_connector():
    """Create S7 connector instance."""
    return S7Connector(ip="192.168.1.100", rack=0, slot=1)


def test_s7_connector_init(s7_connector):
    """Test S7 connector initialization."""
    assert s7_connector.ip == "192.168.1.100"
    assert s7_connector.rack == 0
    assert s7_connector.slot == 1
    assert s7_connector.connected is False


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_s7_connect_success(mock_client_class, s7_connector):
    """Test successful connection to S7 PLC."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    result = s7_connector.connect()
    
    assert result is True
    assert s7_connector.connected is True
    mock_client.set_connection_params.assert_called_once()


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_s7_connect_failure(mock_client_class, s7_connector):
    """Test failed connection to S7 PLC."""
    mock_client_class.side_effect = Exception("Connection failed")
    
    result = s7_connector.connect()
    
    assert result is False
    assert s7_connector.connected is False
    assert s7_connector.last_error is not None


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_s7_disconnect(mock_client_class, s7_connector):
    """Test disconnection from S7 PLC."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    s7_connector.client = mock_client
    s7_connector.connected = True
    
    result = s7_connector.disconnect()
    
    assert result is True
    assert s7_connector.connected is False
    mock_client.disconnect.assert_called_once()


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_read_db_success(mock_client_class, s7_connector):
    """Test reading data block."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    mock_client.db_read.return_value = b'\x01\x02\x03\x04'
    
    s7_connector.connect()
    data = s7_connector.read_db(db_number=1, start=0, size=4)
    
    assert data == b'\x01\x02\x03\x04'
    mock_client.db_read.assert_called_once_with(1, 0, 4)


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_write_db_success(mock_client_class, s7_connector):
    """Test writing to data block."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    mock_client.db_write.return_value = None
    
    s7_connector.connect()
    result = s7_connector.write_db(db_number=1, start=0, data=b'\x01\x02')
    
    assert result is True
    mock_client.db_write.assert_called_once_with(1, 0, b'\x01\x02')


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_read_db_real(mock_client_class, s7_connector):
    """Test reading REAL value from DB."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    mock_client.db_read.return_value = b'\x00\x00\x80\x3f'  # 1.0 in float
    
    s7_connector.connect()
    value = s7_connector.read_db_real(db_number=1, start=0)
    
    assert value is not None
    assert abs(value - 1.0) < 0.01


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_read_db_dint(mock_client_class, s7_connector):
    """Test reading DINT value from DB."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    mock_client.db_read.return_value = b'\x64\x00\x00\x00'  # 100 in int32
    
    s7_connector.connect()
    value = s7_connector.read_db_dint(db_number=1, start=0)
    
    assert value is not None
    assert value == 100


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_read_db_bool(mock_client_class, s7_connector):
    """Test reading BOOL value from DB."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    mock_client.db_read.return_value = b'\x01'
    
    s7_connector.connect()
    value = s7_connector.read_db_bool(db_number=1, start=0, bit=0)
    
    assert value is True


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_read_merkers(mock_client_class, s7_connector):
    """Test reading Merkers."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    mock_client.mb_read.return_value = b'\x01\x02\x03\x04'
    
    s7_connector.connect()
    data = s7_connector.read_merkers(start=0, size=4)
    
    assert data == b'\x01\x02\x03\x04'
    mock_client.mb_read.assert_called_once()


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_read_inputs(mock_client_class, s7_connector):
    """Test reading Inputs."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    mock_client.eb_read.return_value = b'\x01\x02'
    
    s7_connector.connect()
    data = s7_connector.read_inputs(start=0, size=2)
    
    assert data == b'\x01\x02'
    mock_client.eb_read.assert_called_once()


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_read_outputs(mock_client_class, s7_connector):
    """Test reading Outputs."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    mock_client.ab_read.return_value = b'\x01\x02'
    
    s7_connector.connect()
    data = s7_connector.read_outputs(start=0, size=2)
    
    assert data == b'\x01\x02'
    mock_client.ab_read.assert_called_once()


@patch('backend.adapters.s7_connector.snap7.client.Client')
def test_context_manager(mock_client_class, s7_connector):
    """Test S7 connector as context manager."""
    mock_client = Mock()
    mock_client_class.return_value = mock_client
    mock_client.connect.return_value = None
    
    with s7_connector as connector:
        assert connector.connected is True
    
    assert s7_connector.connected is False
    mock_client.disconnect.assert_called_once()


def test_get_last_error(s7_connector):
    """Test getting last error."""
    s7_connector.last_error = "Test error"
    assert s7_connector.get_last_error() == "Test error"
