import pytest
from adapters.modbus import ModbusAdapter
from adapters.opc_ua import OPCUAAdapter
from adapters.s7_connector import S7Connector

def test_modbus_adapter():
    adapter = ModbusAdapter(host="localhost", port=502)
    assert adapter.host == "localhost"
    assert hasattr(adapter, 'connect')
    assert hasattr(adapter, 'read_registers')

def test_opc_ua_adapter():
    adapter = OPCUAAdapter(endpoint_url="opc.tcp://localhost:4840")
    assert adapter.endpoint_url == "opc.tcp://localhost:4840"
    assert hasattr(adapter, 'connect')
    assert hasattr(adapter, 'read_node')

def test_s7_connector():
    connector = S7Connector(ip="192.168.0.1")
    assert connector.ip == "192.168.0.1"
    assert hasattr(connector, 'connect')
    assert hasattr(connector, 'read_db')
