"""
Modbus TCP/RTU Adapter for OMAYA
Standard industrial communication protocol implementation
"""
import logging
from typing import List, Optional, Union
from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

logger = logging.getLogger(__name__)

class ModbusAdapter:
    def __init__(self, host: str = 'localhost', port: int = 502, mode: str = 'tcp', timeout: int = 5):
        self.host = host
        self.port = port
        self.mode = mode
        self.timeout = timeout
        self.client = None

    def connect(self) -> bool:
        if self.mode == 'tcp':
            self.client = ModbusTcpClient(self.host, port=self.port, timeout=self.timeout)
        else:
            self.client = ModbusSerialClient(port=self.host, baudrate=9600, timeout=self.timeout)
        
        return self.client.connect()

    def disconnect(self):
        if self.client:
            self.client.close()

    def read_holding_registers(self, address: int, count: int, slave: int = 1) -> List[int]:
        if not self.client: return []
        result = self.client.read_holding_registers(address, count, slave=slave)
        if result.isError():
            logger.error(f"Modbus error reading registers at {address}: {result}")
            return []
        return result.registers

    def read_input_registers(self, address: int, count: int, slave: int = 1) -> List[int]:
        if not self.client: return []
        result = self.client.read_input_registers(address, count, slave=slave)
        if result.isError():
            return []
        return result.registers

    def read_coils(self, address: int, count: int, slave: int = 1) -> List[bool]:
        if not self.client: return []
        result = self.client.read_coils(address, count, slave=slave)
        if result.isError():
            return []
        return result.bits

    def read_discrete_inputs(self, address: int, count: int, slave: int = 1) -> List[bool]:
        if not self.client: return []
        result = self.client.read_discrete_inputs(address, count, slave=slave)
        if result.isError():
            return []
        return result.bits

    def write_register(self, address: int, value: int, slave: int = 1) -> bool:
        if not self.client: return False
        result = self.client.write_register(address, value, slave=slave)
        return not result.isError()

    def write_registers(self, address: int, values: List[int], slave: int = 1) -> bool:
        if not self.client: return False
        result = self.client.write_registers(address, values, slave=slave)
        return not result.isError()

    def write_coil(self, address: int, value: bool, slave: int = 1) -> bool:
        if not self.client: return False
        result = self.client.write_coil(address, value, slave=slave)
        return not result.isError()

    def read_float(self, address: int, slave: int = 1, byte_order: str = 'big') -> float:
        """Read 32-bit float from two registers"""
        registers = self.read_holding_registers(address, 2, slave=slave)
        if not registers: return 0.0

        bo = Endian.BIG if byte_order == 'big' else Endian.LITTLE
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=bo, wordorder=Endian.BIG)
        return decoder.decode_32bit_float()

    def write_float(self, address: int, value: float, slave: int = 1, byte_order: str = 'big') -> bool:
        """Write 32-bit float to two registers"""
        bo = Endian.BIG if byte_order == 'big' else Endian.LITTLE
        builder = BinaryPayloadBuilder(byteorder=bo, wordorder=Endian.BIG)
        builder.add_32bit_float(value)
        registers = builder.to_registers()
        return self.write_registers(address, registers, slave=slave)

    def read_int32(self, address: int, slave: int = 1, byte_order: str = 'big') -> int:
        """Read 32-bit integer from two registers"""
        registers = self.read_holding_registers(address, 2, slave=slave)
        if not registers: return 0

        bo = Endian.BIG if byte_order == 'big' else Endian.LITTLE
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=bo, wordorder=Endian.BIG)
        return decoder.decode_32bit_int()
