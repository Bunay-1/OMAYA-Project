"""
Siemens S7 Connector for OMAYA Platform
Direct communication with S7-1200/1500 PLCs.
"""
from typing import Dict, Any, Optional, List
import logging
import struct
from datetime import datetime
import snap7
from snap7.util import *

logger = logging.getLogger(__name__)

class S7Connector:
    """
    Siemens S7-1200/1500 PLC Connector
    Supports reading/writing DBs, Merkers, Inputs, Outputs
    """
    
    def __init__(self, ip: str, rack: int = 0, slot: int = 1, timeout: int = 1000):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.timeout = timeout
        self.client = snap7.client.Client()
        self.connected = False
        self.last_error: Optional[str] = None
        
    def connect(self) -> bool:
        """Connect to Siemens PLC."""
        try:
            logger.info(f"Connecting to Siemens S7 PLC at {self.ip} (rack={self.rack}, slot={self.slot})")
            self.client.set_connection_params(self.ip, self.rack, self.slot)
            self.client.set_connection_type(1)  # 1 = PG, 2 = OP
            self.client.connect()
            self.connected = True
            self.last_error = None
            logger.info(f"Successfully connected to {self.ip}")
            return True
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            logger.error(f"Failed to connect to S7 PLC at {self.ip}: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from PLC."""
        try:
            if self.connected:
                self.client.disconnect()
                self.connected = False
                logger.info(f"Disconnected from {self.ip}")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from {self.ip}: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connected
    
    def read_db(self, db_number: int, start: int, size: int) -> Optional[bytes]:
        """
        Read data block from PLC.
        
        Args:
            db_number: Data block number
            start: Start byte offset
            size: Number of bytes to read
            
        Returns:
            Raw bytes data or None on error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            data = self.client.db_read(db_number, start, size)
            logger.debug(f"Read DB{db_number} start={start} size={size}")
            return data
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading DB{db_number}: {e}")
            return None
    
    def write_db(self, db_number: int, start: int, data: bytes) -> bool:
        """
        Write data to PLC data block.
        
        Args:
            db_number: Data block number
            start: Start byte offset
            data: Bytes to write
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            self.client.db_write(db_number, start, data)
            logger.debug(f"Wrote DB{db_number} start={start} size={len(data)}")
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error writing DB{db_number}: {e}")
            return False
    
    def read_db_real(self, db_number: int, start: int) -> Optional[float]:
        """Read a REAL (float) value from DB."""
        data = self.read_db(db_number, start, 4)
        if data:
            return get_real(data, 0)
        return None
    
    def write_db_real(self, db_number: int, start: int, value: float) -> bool:
        """Write a REAL (float) value to DB."""
        data = bytearray(4)
        set_real(data, 0, value)
        return self.write_db(db_number, start, data)
    
    def read_db_dint(self, db_number: int, start: int) -> Optional[int]:
        """Read a DINT (32-bit integer) value from DB."""
        data = self.read_db(db_number, start, 4)
        if data:
            return get_dint(data, 0)
        return None
    
    def write_db_dint(self, db_number: int, start: int, value: int) -> bool:
        """Write a DINT (32-bit integer) value to DB."""
        data = bytearray(4)
        set_dint(data, 0, value)
        return self.write_db(db_number, start, data)
    
    def read_db_bool(self, db_number: int, start: int, bit: int = 0) -> Optional[bool]:
        """Read a BOOL value from DB."""
        data = self.read_db(db_number, start, 1)
        if data:
            return get_bool(data, 0, bit)
        return None
    
    def write_db_bool(self, db_number: int, start: int, bit: int = 0, value: bool = True) -> bool:
        """Write a BOOL value to DB."""
        data = bytearray(1)
        set_bool(data, 0, bit, value)
        return self.write_db(db_number, start, data)
    
    def read_merkers(self, start: int, size: int) -> Optional[bytes]:
        """Read Merkers (M) memory area."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            data = self.client.mb_read(start, size)
            logger.debug(f"Read Merkers start={start} size={size}")
            return data
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading Merkers: {e}")
            return None
    
    def read_inputs(self, start: int, size: int) -> Optional[bytes]:
        """Read Inputs (I) area."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            data = self.client.eb_read(start, size)
            logger.debug(f"Read Inputs start={start} size={size}")
            return data
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading Inputs: {e}")
            return None
    
    def read_outputs(self, start: int, size: int) -> Optional[bytes]:
        """Read Outputs (Q) area."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            data = self.client.ab_read(start, size)
            logger.debug(f"Read Outputs start={start} size={size}")
            return data
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading Outputs: {e}")
            return None
    
    def write_merkers(self, start: int, data: bytes) -> bool:
        """Write Merkers (M) memory area."""
        if not self.connected:
            if not self.connect():
                return False

        try:
            self.client.mb_write(start, data)
            logger.debug(f"Wrote Merkers start={start} size={len(data)}")
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error writing Merkers: {e}")
            return False

    def write_outputs(self, start: int, data: bytes) -> bool:
        """Write Outputs (Q) area."""
        if not self.connected:
            if not self.connect():
                return False

        try:
            self.client.ab_write(start, data)
            logger.debug(f"Wrote Outputs start={start} size={len(data)}")
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error writing Outputs: {e}")
            return False

    def read_plc_info(self) -> Optional[Dict[str, Any]]:
        """Read PLC system information."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            info = {
                'module_type': self.client.get_cpu_info().ModuleTypeName,
                'serial_number': self.client.get_cpu_info().SerialNumber,
                'as_name': self.client.get_cpu_info().ASName,
                'copyright': self.client.get_cpu_info().Copyright,
                'module_name': self.client.get_cpu_info().ModuleName,
            }
            return info
        except Exception as e:
            logger.error(f"Error reading PLC info: {e}")
            return None
    
    def read_szl(self, ssl_id: int, index: int) -> Optional[bytes]:
        """Read System Status List (SZL)."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            data = self.client.read_szl(ssl_id, index)
            return data
        except Exception as e:
            logger.error(f"Error reading SZL: {e}")
            return None
    
    def get_plc_time(self) -> Optional[datetime]:
        """Read PLC system time."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            data = self.client.get_plc_datetime()
            return data
        except Exception as e:
            logger.error(f"Error reading PLC time: {e}")
            return None
    
    def set_plc_time(self, dt: datetime = None) -> bool:
        """Set PLC system time."""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            if dt is None:
                dt = datetime.now()
            self.client.set_plc_datetime(dt)
            logger.info(f"Set PLC time to {dt}")
            return True
        except Exception as e:
            logger.error(f"Error setting PLC time: {e}")
            return False
    
    def read_multi_vars(self, items: List[Dict[str, Any]]) -> List[Optional[Any]]:
        """
        Read multiple variables in one request.
        
        Args:
            items: List of dicts with keys: area, db_number, start, size, word_len
            
        Returns:
            List of values or None for failed reads
        """
        if not self.connected:
            if not self.connect():
                return [None] * len(items)
        
        try:
            results = self.client.read_multi_vars(items)
            return results
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading multi vars: {e}")
            return [None] * len(items)
    
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
