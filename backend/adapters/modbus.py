"""
Modbus TCP/RTU Adapter for OMAYA Platform
Universal connectivity for legacy industrial hardware.
"""
from typing import Dict, Any, Optional, List, Union
import logging
from datetime import datetime
from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu.register_message import ReadHoldingRegistersResponse, ReadInputRegistersResponse

logger = logging.getLogger(__name__)

class ModbusAdapter:
    """
    Modbus TCP/RTU Adapter
    Supports both TCP and RTU (serial) connections
    """
    
    def __init__(self, host: str = None, port: int = 502, 
                 serial_port: str = None, baudrate: int = 9600,
                 unit: int = 1, timeout: int = 3):
        """
        Initialize Modbus adapter.
        
        Args:
            host: IP address for TCP connection
            port: Port for TCP connection (default 502)
            serial_port: Serial port for RTU connection (e.g., '/dev/ttyUSB0')
            baudrate: Baudrate for RTU connection (default 9600)
            unit: Slave/unit ID (default 1)
            timeout: Connection timeout in seconds (default 3)
        """
        self.host = host
        self.port = port
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.unit = unit
        self.timeout = timeout
        self.client = None
        self.connected = False
        self.connection_type = 'tcp' if host else 'rtu'
        self.last_error: Optional[str] = None
        
    def connect(self) -> bool:
        """Establish Modbus connection."""
        try:
            if self.connection_type == 'tcp':
                logger.info(f"Connecting to Modbus TCP at {self.host}:{self.port}")
                self.client = ModbusTcpClient(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout
                )
            else:
                logger.info(f"Connecting to Modbus RTU at {self.serial_port}")
                self.client = ModbusSerialClient(
                    port=self.serial_port,
                    baudrate=self.baudrate,
                    timeout=self.timeout
                )
            
            if self.client.connect():
                self.connected = True
                self.last_error = None
                logger.info(f"Successfully connected to Modbus device")
                return True
            else:
                self.connected = False
                self.last_error = "Connection failed"
                logger.error(f"Failed to connect to Modbus device")
                return False
                
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            logger.error(f"Error connecting to Modbus: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Modbus device."""
        try:
            if self.client and self.connected:
                self.client.close()
                self.connected = False
                logger.info("Disconnected from Modbus device")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Modbus: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connected
    
    def read_holding_registers(self, address: int, count: int, 
                               slave: int = None) -> Optional[List[int]]:
        """
        Read holding registers (function code 0x03).
        
        Args:
            address: Starting register address
            count: Number of registers to read
            slave: Slave ID (overrides default if provided)
            
        Returns:
            List of register values or None on error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            slave_id = slave if slave is not None else self.unit
            response = self.client.read_holding_registers(
                address=address,
                count=count,
                slave=slave_id
            )
            
            if not response.isError():
                return response.registers
            else:
                self.last_error = f"Modbus error: {response}"
                logger.error(f"Error reading holding registers: {response}")
                return None
                
        except ModbusException as e:
            self.last_error = str(e)
            logger.error(f"Modbus exception reading holding registers: {e}")
            return None
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading holding registers: {e}")
            return None
    
    def read_input_registers(self, address: int, count: int,
                             slave: int = None) -> Optional[List[int]]:
        """
        Read input registers (function code 0x04).
        
        Args:
            address: Starting register address
            count: Number of registers to read
            slave: Slave ID (overrides default if provided)
            
        Returns:
            List of register values or None on error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            slave_id = slave if slave is not None else self.unit
            response = self.client.read_input_registers(
                address=address,
                count=count,
                slave=slave_id
            )
            
            if not response.isError():
                return response.registers
            else:
                self.last_error = f"Modbus error: {response}"
                logger.error(f"Error reading input registers: {response}")
                return None
                
        except ModbusException as e:
            self.last_error = str(e)
            logger.error(f"Modbus exception reading input registers: {e}")
            return None
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading input registers: {e}")
            return None
    
    def read_coils(self, address: int, count: int,
                   slave: int = None) -> Optional[List[bool]]:
        """
        Read coils (function code 0x01).
        
        Args:
            address: Starting coil address
            count: Number of coils to read
            slave: Slave ID (overrides default if provided)
            
        Returns:
            List of coil values or None on error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            slave_id = slave if slave is not None else self.unit
            response = self.client.read_coils(
                address=address,
                count=count,
                slave=slave_id
            )
            
            if not response.isError():
                return response.bits
            else:
                self.last_error = f"Modbus error: {response}"
                logger.error(f"Error reading coils: {response}")
                return None
                
        except ModbusException as e:
            self.last_error = str(e)
            logger.error(f"Modbus exception reading coils: {e}")
            return None
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading coils: {e}")
            return None
    
    def read_discrete_inputs(self, address: int, count: int,
                             slave: int = None) -> Optional[List[bool]]:
        """
        Read discrete inputs (function code 0x02).
        
        Args:
            address: Starting input address
            count: Number of inputs to read
            slave: Slave ID (overrides default if provided)
            
        Returns:
            List of input values or None on error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            slave_id = slave if slave is not None else self.unit
            response = self.client.read_discrete_inputs(
                address=address,
                count=count,
                slave=slave_id
            )
            
            if not response.isError():
                return response.bits
            else:
                self.last_error = f"Modbus error: {response}"
                logger.error(f"Error reading discrete inputs: {response}")
                return None
                
        except ModbusException as e:
            self.last_error = str(e)
            logger.error(f"Modbus exception reading discrete inputs: {e}")
            return None
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading discrete inputs: {e}")
            return None
    
    def write_register(self, address: int, value: int,
                       slave: int = None) -> bool:
        """
        Write single register (function code 0x06).
        
        Args:
            address: Register address
            value: Value写入 (0-65535)
            slave: Slave ID (overrides default if provided)
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            slave_id = slave if slave is not None else self.unit
            response = self.client.write_register(
                address=address,
                value=value,
                slave=slave_id
            )
            
            if not response.isError():
                logger.debug(f"Wrote register {address} = {value}")
                return True
            else:
                self.last_error = f"Modbus error: {response}"
                logger.error(f"Error writing register: {response}")
                return False
                
        except ModbusException as e:
            self.last_error = str(e)
            logger.error(f"Modbus exception writing register: {e}")
            return False
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error writing register: {e}")
            return False
    
    def write_registers(self, address: int, values: List[int],
                        slave: int = None) -> bool:
        """
        Write multiple registers (function code 0x10).
        
        Args:
            address: Starting register address
            values: List of values to write
            slave: Slave ID (overrides default if provided)
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            slave_id = slave if slave is not None else self.unit
            response = self.client.write_registers(
                address=address,
                values=values,
                slave=slave_id
            )
            
            if not response.isError():
                logger.debug(f"Wrote {len(values)} registers starting at {address}")
                return True
            else:
                self.last_error = f"Modbus error: {response}"
                logger.error(f"Error writing registers: {response}")
                return False
                
        except ModbusException as e:
            self.last_error = str(e)
            logger.error(f"Modbus exception writing registers: {e}")
            return False
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error writing registers: {e}")
            return False
    
    def write_coil(self, address: int, value: bool,
                   slave: int = None) -> bool:
        """
        Write single coil (function code 0x05).
        
        Args:
            address: Coil address
            value: Value to write (True/False)
            slave: Slave ID (overrides default if provided)
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            slave_id = slave if slave is not None else self.unit
            response = self.client.write_coil(
                address=address,
                value=value,
                slave=slave_id
            )
            
            if not response.isError():
                logger.debug(f"Wrote coil {address} = {value}")
                return True
            else:
                self.last_error = f"Modbus error: {response}"
                logger.error(f"Error writing coil: {response}")
                return False
                
        except ModbusException as e:
            self.last_error = str(e)
            logger.error(f"Modbus exception writing coil: {e}")
            return False
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error writing coil: {e}")
            return False
    
    def read_float(self, address: int, slave: int = None, 
                   byte_order: str = 'big') -> Optional[float]:
        """
        Read a 32-bit float from two consecutive registers.
        
        Args:
            address: Starting register address
            slave: Slave ID (overrides default if provided)
            byte_order: 'big' or 'little' endian
            
        Returns:
            Float value or None on error
        """
        registers = self.read_holding_registers(address, 2, slave)
        if registers is None:
            return None
        
        try:
            import struct
            # Combine two 16-bit registers into 32-bit
            if byte_order == 'big':
                value = struct.unpack('>f', struct.pack('>HH', *registers))[0]
            else:
                value = struct.unpack('<f', struct.pack('<HH', *registers))[0]
            return value
        except Exception as e:
            logger.error(f"Error converting registers to float: {e}")
            return None
    
    def write_float(self, address: int, value: float, slave: int = None,
                    byte_order: str = 'big') -> bool:
        """
        Write a 32-bit float to two consecutive registers.
        
        Args:
            address: Starting register address
            value: Float value to write
            slave: Slave ID (overrides default if provided)
            byte_order: 'big' or 'little' endian
            
        Returns:
            True on success, False on error
        """
        try:
            import struct
            if byte_order == 'big':
                registers = struct.unpack('>HH', struct.pack('>f', value))
            else:
                registers = struct.unpack('<HH', struct.pack('<f', value))
            return self.write_registers(address, list(registers), slave)
        except Exception as e:
            logger.error(f"Error converting float to registers: {e}")
            return False
    
    def read_int32(self, address: int, slave: int = None,
                   byte_order: str = 'big') -> Optional[int]:
        """
        Read a 32-bit integer from two consecutive registers.
        
        Args:
            address: Starting register address
            slave: Slave ID (overrides default if provided)
            byte_order: 'big' or 'little' endian
            
        Returns:
            Integer value or None on error
        """
        registers = self.read_holding_registers(address, 2, slave)
        if registers is None:
            return None
        
        try:
            import struct
            if byte_order == 'big':
                value = struct.unpack('>i', struct.pack('>HH', *registers))[0]
            else:
                value = struct.unpack('<i', struct.pack('<HH', *registers))[0]
            return value
        except Exception as e:
            logger.error(f"Error converting registers to int32: {e}")
            return None
    
    def read_device_info(self, slave: int = None) -> Optional[Dict[str, Any]]:
        """
        Read device information (if supported).
        
        Args:
            slave: Slave ID (overrides default if provided)
            
        Returns:
            Device info dict or None on error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            slave_id = slave if slave is not None else self.unit
            response = self.client.read_device_info(slave_id)
            
            if not response.isError():
                return {
                    'vendor_name': response.information[0] if len(response.information) > 0 else None,
                    'product_code': response.information[1] if len(response.information) > 1 else None,
                    'major_minor_revision': response.information[2] if len(response.information) > 2 else None,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.debug("Device info not supported by device")
                return None
                
        except Exception as e:
            logger.error(f"Error reading device info: {e}")
            return None
    
    def get_last_error(self) -> Optional[str]:
        """Get last error message."""
        return self.last_error
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
