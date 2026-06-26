"""
Tests for Fanuc FOCAS Connector
"""
import pytest
from backend.adapters.fanuc_focas import FanucConnector, FanucAxis, FanucMode
from unittest.mock import Mock, patch


@pytest.fixture
def fanuc_connector():
    """Create Fanuc connector instance."""
    connector = FanucConnector(ip="192.168.1.100", port=8193)
    # Mock fwlib to avoid real library loading issues
    connector.fwlib = Mock()
    return connector


def test_fanuc_connector_init(fanuc_connector):
    """Test Fanuc connector initialization."""
    assert fanuc_connector.ip == "192.168.1.100"
    assert fanuc_connector.port == 8193
    assert fanuc_connector.connected is False


def test_fanuc_connect_simulation_mode(fanuc_connector):
    """Test connection in simulation mode."""
    fanuc_connector.fwlib = None # Force simulation mode
    result = fanuc_connector.connect()
    
    assert result is True
    assert fanuc_connector.connected is True


def test_fanuc_disconnect(fanuc_connector):
    """Test disconnection."""
    fanuc_connector.handle = 1
    fanuc_connector.connected = True
    result = fanuc_connector.disconnect()
    
    assert result is True
    assert fanuc_connector.connected is False
    fanuc_connector.fwlib.cnc_freelibhndl.assert_called_once()


def test_read_axis_position_simulation(fanuc_connector):
    """Test reading axis position in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    position = fanuc_connector.read_axis_position(FanucAxis.X)
    
    assert position is not None
    assert isinstance(position, float)


def test_read_all_axes_simulation(fanuc_connector):
    """Test reading all axes in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    positions = fanuc_connector.read_all_axes()
    
    assert positions is not None
    assert isinstance(positions, dict)
    assert 'X' in positions


def test_read_spindle_speed_simulation(fanuc_connector):
    """Test reading spindle speed in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    speed = fanuc_connector.read_spindle_speed()
    
    assert speed is not None
    assert isinstance(speed, int)


def test_read_feed_rate_simulation(fanuc_connector):
    """Test reading feed rate in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    feed = fanuc_connector.read_feed_rate()
    
    assert feed is not None
    assert isinstance(feed, float)


def test_read_operation_mode_simulation(fanuc_connector):
    """Test reading operation mode in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    mode = fanuc_connector.read_operation_mode()
    
    assert mode is not None
    assert isinstance(mode, FanucMode)


def test_read_alarms_simulation(fanuc_connector):
    """Test reading alarms in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    alarms = fanuc_connector.read_alarms()
    
    assert alarms is None or isinstance(alarms, list)


def test_read_tool_info_simulation(fanuc_connector):
    """Test reading tool info in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    tool_info = fanuc_connector.read_tool_info()
    
    assert tool_info is not None
    assert 'tool_number' in tool_info


def test_read_program_name_simulation(fanuc_connector):
    """Test reading program name in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    prog_name = fanuc_connector.read_program_name()
    
    assert prog_name is not None
    assert isinstance(prog_name, str)


def test_read_machine_status_simulation(fanuc_connector):
    """Test reading machine status in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    status = fanuc_connector.read_machine_status()
    
    assert status is not None
    assert 'ip' in status
    assert 'axes' in status
    assert 'spindle_speed' in status


def test_write_macro_variable_simulation(fanuc_connector):
    """Test writing macro variable in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    result = fanuc_connector.write_macro_variable(number=1, value=100.0)
    
    assert result is True


def test_read_macro_variable_simulation(fanuc_connector):
    """Test reading macro variable in simulation mode."""
    fanuc_connector.fwlib = None
    fanuc_connector.connected = True
    value = fanuc_connector.read_macro_variable(number=1)
    
    assert value is not None
    assert isinstance(value, float)


def test_fanuc_axis_enum():
    """Test FanucAxis enum."""
    assert FanucAxis.X.value == 0
    assert FanucAxis.Y.value == 1
    assert FanucAxis.Z.value == 2


def test_fanuc_mode_enum():
    """Test FanucMode enum."""
    assert FanucMode.AUTO.value == 0
    assert FanucMode.EDIT.value == 1
    assert FanucMode.MDI.value == 2


def test_context_manager(fanuc_connector):
    """Test Fanuc connector as context manager."""
    with patch.object(FanucConnector, 'connect', side_effect=lambda: setattr(fanuc_connector, 'connected', True) or True):
        with patch.object(FanucConnector, 'disconnect', side_effect=lambda: setattr(fanuc_connector, 'connected', False) or True):
            with fanuc_connector as connector:
                assert connector.connected is True

            assert connector.connected is False


def test_get_last_error(fanuc_connector):
    """Test getting last error."""
    fanuc_connector.last_error = "Test error"
    assert fanuc_connector.get_last_error() == "Test error"
