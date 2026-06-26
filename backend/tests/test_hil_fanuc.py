"""
Hardware-in-the-Loop Tests for Fanuc FOCAS Connector
Tests with simulated CNC behavior
"""
import pytest
from backend.adapters.fanuc_focas import FanucConnector, FanucAxis, FanucMode
from unittest.mock import Mock, patch
from datetime import datetime

@pytest.fixture
def simulated_fanuc_cnc():
    """Create simulated Fanuc CNC for HIL testing."""
    cnc = Mock()
    cnc.positions = {axis.value: 0.0 for axis in FanucAxis}
    cnc.spindle_speed = 0
    cnc.feed_rate = 0
    cnc.mode = FanucMode.AUTO.value
    cnc.macros = {}

    def cnc_absolute(handle, axis, pos_ref):
        if axis in cnc.positions:
            pos_ref._obj.value = cnc.positions[axis]
            return 0
        return -1

    def cnc_rdspeed(handle, type, speed_ref):
        speed_ref._obj.value = cnc.spindle_speed
        return 0

    def cnc_actf(handle, feed_ref):
        feed_ref._obj.value = int(cnc.feed_rate * 100)
        return 0

    def cnc_statmode(handle, mode_ref):
        mode_ref._obj.value = cnc.mode
        return 0

    def cnc_wrmacro(handle, number, val_ref):
        cnc.macros[number] = val_ref._obj.value
        return 0

    def cnc_rdmacro(handle, number, val_ref):
        if number in cnc.macros:
            val_ref._obj.value = cnc.macros[number]
            return 0
        val_ref._obj.value = 0.0
        return 0

    cnc.cnc_absolute = cnc_absolute
    cnc.cnc_rdspeed = cnc_rdspeed
    cnc.cnc_actf = cnc_actf
    cnc.cnc_statmode = cnc_statmode
    cnc.cnc_wrmacro = cnc_wrmacro
    cnc.cnc_rdmacro = cnc_rdmacro

    return cnc

@pytest.fixture
def fanuc_connector_with_sim(simulated_fanuc_cnc):
    """Create Fanuc connector with simulated CNC."""
    connector = FanucConnector(ip="192.168.1.100")
    connector.fwlib = simulated_fanuc_cnc
    connector.handle = 1
    connector.connected = True
    return connector

def test_hil_fanuc_read_position(fanuc_connector_with_sim, simulated_fanuc_cnc):
    """HIL test: Read axis position."""
    simulated_fanuc_cnc.positions[FanucAxis.X.value] = 123.456
    pos = fanuc_connector_with_sim.read_axis_position(FanucAxis.X)
    assert pos == 123.456

def test_hil_fanuc_read_spindle_speed(fanuc_connector_with_sim, simulated_fanuc_cnc):
    """HIL test: Read spindle speed."""
    simulated_fanuc_cnc.spindle_speed = 10000
    speed = fanuc_connector_with_sim.read_spindle_speed()
    assert speed == 10000

def test_hil_fanuc_read_feed_rate(fanuc_connector_with_sim, simulated_fanuc_cnc):
    """HIL test: Read feed rate."""
    simulated_fanuc_cnc.feed_rate = 1500.5
    feed = fanuc_connector_with_sim.read_feed_rate()
    assert feed == 1500.5

def test_hil_fanuc_read_mode(fanuc_connector_with_sim, simulated_fanuc_cnc):
    """HIL test: Read operation mode."""
    simulated_fanuc_cnc.mode = FanucMode.MDI.value
    mode = fanuc_connector_with_sim.read_operation_mode()
    assert mode == FanucMode.MDI

def test_hil_fanuc_macros(fanuc_connector_with_sim):
    """HIL test: Read/Write macro variables."""
    result = fanuc_connector_with_sim.write_macro_variable(number=500, value=99.9)
    assert result is True

    val = fanuc_connector_with_sim.read_macro_variable(number=500)
    assert val == 99.9

def test_hil_fanuc_full_status(fanuc_connector_with_sim, simulated_fanuc_cnc):
    """HIL test: Comprehensive status read."""
    simulated_fanuc_cnc.positions[FanucAxis.Z.value] = -50.0
    simulated_fanuc_cnc.spindle_speed = 5000

    status = fanuc_connector_with_sim.read_machine_status()
    assert status['connected'] is True
    assert status['axes']['Z'] == -50.0
    assert status['spindle_speed'] == 5000
