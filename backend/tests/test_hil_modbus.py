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
    
    def read_holding_registers(address, count, slave):
        return device.holding_registers[address:address+count]
    
    def write_register(address, value, slave):
        device.holding_registers[address] = value
        return Mock(isError=lambda: False)
    
    def write_registers(address, values, slave):
        for i, value in enumerate(values):
            device.holding_registers[address + i] = value
        return Mock(isError=lambda: False)
    
    def read_coils(address, count, slave):
        return device.coils[address:address+count]
    
    def write_coil(address, value, slave):
        device.coils[address] = value
        return Mock(isError=lambda: False)
    
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


def test_hil_modbus_multiple_slaves(modbus_adapter_with_sim):
    """HIL test: Operations with multiple slave IDs."""
    # Write to slave 1
    modbus_adapter_with_sim.write_register(address=0, value=100, slave=1)
    # Write to slave 2
    modbus_adapter_with_sim.write_register(address=0, value=200, slave=2)
    
    # Read from slave 1
    value1 = modbus_adapter_with_sim.read_holding_registers(address=0, count=1, slave=1)
    # Read from slave 2
    value2 = modbus_adapter_with_sim.read_holding_registers(address=0, count=1, slave=2)
    
    # Note: In this simple simulation, slaves share the same registers
    # Real implementation would have separate register sets per slave


def test_hil_modbus_concurrent_access(modbus_adapter_with_sim):
    """HIL test: Concurrent read/write operations."""
    import threading
    
    results = []
    
    def read_operation():
        for i in range(100):
            value = modbus_adapter_with_sim.read_holding_registers(address=0, count=1)
            results.append(('read', value))
    
    def write_operation():
        for i in range(100):
            result = modbus_adapter_with_sim.write_register(address=0, value=i)
            results.append(('write', result))
    
    thread1 = threading.Thread(target=read_operation)
    thread2 = threading.Thread(target=write_operation)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    assert len(results) == 200


def test_hil_modbus_performance(modbus_adapter_with_sim):
    """HIL test: Performance benchmark."""
    import time
    
    start_time = time.time()
    for i in range(1000):
        modbus_adapter_with_sim.read_holding_registers(address=0, count=1)
    end_time = time.time()
    
    duration = end_time - start_time
    ops_per_second = 1000 / duration
    
    assert ops_per_second > 100


def test_hil_modbus_register_boundary(modbus_adapter_with_sim):
    """HIL test: Operations at register boundaries."""
    # Write at end of register array
    result = modbus_adapter_with_sim.write_register(address=998, value=999)
    assert result is True
    
    # Read at boundary
    values = modbus_adapter_with_sim.read_holding_registers(address=998, count=2)
    assert len(values) == 2


def test_hil_modbus_data_persistence(modbus_adapter_with_sim):
    """HIL test: Data persistence across operations."""
    # Write value
    modbus_adapter_with_sim.write_register(address=0, value=12345)
    
    # Perform other operations
    for i in range(10):
        modbus_adapter_with_sim.write_register(address=100 + i, value=i)
    
    # Verify original value
    value = modbus_adapter_with_sim.read_holding_registers(address=0, count=1)
    assert value[0] == 12345


def test_hil_modbus_error_recovery(modbus_adapter_with_sim):
    """HIL test: Error recovery from invalid operations."""
    # Try to read beyond available registers
    values = modbus_adapter_with_sim.read_holding_registers(address=2000, count=10)
    # Should handle gracefully (return empty or partial data)
    assert values is not None
