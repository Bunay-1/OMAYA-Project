"""
Hardware-in-the-Loop Tests for Modbus Adapter
Tests with simulated Modbus device behavior
"""
import pytest
from backend.adapters.modbus import ModbusAdapter
from unittest.mock import Mock, MagicMock


@pytest.fixture
def simulated_modbus_device():
    """Create simulated Modbus device for HIL testing."""
    device = Mock()
    device.holding_registers = [0] * 1000
    device.input_registers = [0] * 1000
    device.coils = [False] * 1000
    device.discrete_inputs = [False] * 1000
    
    def create_response(data_attr, address, count):
        resp = Mock()
        resp.isError.return_value = False
        if data_attr == 'registers':
            resp.registers = device.holding_registers[address:address+count]
        else:
            resp.bits = device.coils[address:address+count]
        return resp

    def read_holding_registers(address, count, slave):
        return create_response('registers', address, count)
    
    def write_register(address, value, slave):
        device.holding_registers[address] = value
        resp = Mock()
        resp.isError.return_value = False
        return resp
    
    def write_registers(address, values, slave):
        for i, value in enumerate(values):
            device.holding_registers[address + i] = value
        resp = Mock()
        resp.isError.return_value = False
        return resp
    
    def read_coils(address, count, slave):
        return create_response('bits', address, count)
    
    def write_coil(address, value, slave):
        device.coils[address] = value
        resp = Mock()
        resp.isError.return_value = False
        return resp
    
    device.read_holding_registers = read_holding_registers
    device.write_register = write_register
    device.write_registers = write_registers
    device.read_coils = read_coils
    device.write_coil = write_coil
    
    return device


@pytest.fixture
def modbus_adapter_with_sim(simulated_modbus_device):
    """Create Modbus adapter with simulated device."""
    adapter = ModbusAdapter(host="192.168.1.100", port=502)
    adapter.client = simulated_modbus_device
    adapter.connected = True
    return adapter


def test_hil_modbus_read_holding_registers(modbus_adapter_with_sim):
    """HIL test: Read holding registers."""
    modbus_adapter_with_sim.client.holding_registers[0] = 100
    modbus_adapter_with_sim.client.holding_registers[1] = 200
    
    values = modbus_adapter_with_sim.read_holding_registers(address=0, count=2)
    assert values == [100, 200]


def test_hil_modbus_write_register(modbus_adapter_with_sim):
    """HIL test: Write single register."""
    result = modbus_adapter_with_sim.write_register(address=0, value=42)
    assert result is True
    assert modbus_adapter_with_sim.client.holding_registers[0] == 42


def test_hil_modbus_write_registers(modbus_adapter_with_sim):
    """HIL test: Write multiple registers."""
    result = modbus_adapter_with_sim.write_registers(
        address=0, 
        values=[10, 20, 30, 40]
    )
    assert result is True
    assert modbus_adapter_with_sim.client.holding_registers[0:4] == [10, 20, 30, 40]


def test_hil_modbus_read_float(modbus_adapter_with_sim):
    """HIL test: Read float from registers."""
    import struct
    # Set registers to represent 3.14
    float_bytes = struct.pack('>f', 3.14)
    registers = list(struct.unpack('>HH', float_bytes))
    modbus_adapter_with_sim.client.holding_registers[0:2] = registers
    
    value = modbus_adapter_with_sim.read_float(address=0, byte_order='big')
    assert abs(value - 3.14) < 0.01


def test_hil_modbus_write_float(modbus_adapter_with_sim):
    """HIL test: Write float to registers."""
    result = modbus_adapter_with_sim.write_float(address=0, value=42.5, byte_order='big')
    assert result is True
    
    # Verify
    value = modbus_adapter_with_sim.read_float(address=0, byte_order='big')
    assert abs(value - 42.5) < 0.01


def test_hil_modbus_read_int32(modbus_adapter_with_sim):
    """HIL test: Read int32 from registers."""
    import struct
    # Set registers to represent 100000
    int_bytes = struct.pack('>i', 100000)
    registers = list(struct.unpack('>HH', int_bytes))
    modbus_adapter_with_sim.client.holding_registers[0:2] = registers
    
    value = modbus_adapter_with_sim.read_int32(address=0, byte_order='big')
    assert value == 100000


def test_hil_modbus_read_coils(modbus_adapter_with_sim):
    """HIL test: Read coils."""
    modbus_adapter_with_sim.client.coils[0] = True
    modbus_adapter_with_sim.client.coils[1] = False
    modbus_adapter_with_sim.client.coils[2] = True
    
    values = modbus_adapter_with_sim.read_coils(address=0, count=3)
    assert values == [True, False, True]


def test_hil_modbus_write_coil(modbus_adapter_with_sim):
    """HIL test: Write single coil."""
    result = modbus_adapter_with_sim.write_coil(address=0, value=True)
    assert result is True
    assert modbus_adapter_with_sim.client.coils[0] is True
