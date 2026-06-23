"""
Fanuc FOCAS Connector for OMAYA Platform
Direct communication with Fanuc CNC controllers.
Note: Requires FOCAS library (fwlib32.dll/fwlib64.dll) from Fanuc
"""
from typing import Dict, Any, Optional, List
import logging
import struct
from datetime import datetime
import ctypes
from enum import Enum

logger = logging.getLogger(__name__)

class FanucAxis(Enum):
    """Fanuc axis enumeration."""
    X = 0
    Y = 1
    Z = 2
    A = 3
    B = 4
    C = 5

class FanucMode(Enum):
    """Fanuc operation modes."""
    AUTO = 0
    EDIT = 1
    MDI = 2
    JOG = 3
    HANDLE = 4
    JOG_INC = 5
    TEACH = 6
    MANUAL = 7

class FanucConnector:
    """
    Fanuc FOCAS CNC Controller Connector
    Supports reading/writing CNC data, axis positions, tool info, alarms
    """
    
    def __init__(self, ip: str, port: int = 8193, timeout: int = 10):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.handle = None
        self.connected = False
        self.last_error: Optional[str] = None
        self.fwlib = None
        
        # Try to load FOCAS library
        try:
            # Try to load FOCAS library (platform-specific)
            import platform
            if platform.system() == 'Windows':
                try:
                    self.fwlib = ctypes.WinDLL('fwlib64.dll')
                except:
                    self.fwlib = ctypes.WinDLL('fwlib32.dll')
            else:
                # Linux - would need libfwlib.so
                self.fwlib = ctypes.CDLL('libfwlib.so')
            
            if self.fwlib:
                logger.info("FOCAS library loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load FOCAS library: {e}")
            logger.warning("Fanuc connector will run in simulation mode")
    
    def connect(self) -> bool:
        """Connect to Fanuc CNC controller."""
        try:
            if self.fwlib is None:
                # Simulation mode for development/testing
                logger.info(f"Fanuc connector running in simulation mode for {self.ip}")
                self.connected = True
                self.handle = 1  # Mock handle
                return True
            
            # Real FOCAS connection
            self.handle = self.fwlib.cnc_allclibhndl3(
                self.ip.encode('ascii'),
                self.port,
                self.timeout
            )
            
            if self.handle == -1 or self.handle == 0:
                self.connected = False
                self.last_error = "Failed to connect to Fanuc controller"
                logger.error(f"Failed to connect to Fanuc at {self.ip}")
                return False
            
            self.connected = True
            self.last_error = None
            logger.info(f"Successfully connected to Fanuc CNC at {self.ip}")
            return True
            
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            logger.error(f"Error connecting to Fanuc: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from CNC controller."""
        try:
            if self.connected and self.fwlib and self.handle:
                self.fwlib.cnc_freelibhndl(self.handle)
                self.handle = None
                self.connected = False
                logger.info(f"Disconnected from Fanuc at {self.ip}")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Fanuc: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connected
    
    def read_axis_position(self, axis: FanucAxis) -> Optional[float]:
        """
        Read current axis position.
        
        Args:
            axis: Axis to read (X, Y, Z, A, B, C)
            
        Returns:
            Current position in mm or None on error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            if self.fwlib and self.handle:
                # Real FOCAS call
                pos = ctypes.c_double()
                ret = self.fwlib.cnc_absolute(self.handle, axis.value, ctypes.byref(pos))
                if ret == 0:
                    return pos.value
            else:
                # Simulation mode
                import random
                return random.uniform(0, 500)
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading axis {axis.name}: {e}")
        
        return None
    
    def read_all_axes(self) -> Optional[Dict[str, float]]:
        """Read all axis positions."""
        positions = {}
        for axis in FanucAxis:
            pos = self.read_axis_position(axis)
            if pos is not None:
                positions[axis.name] = pos
        return positions if positions else None
    
    def read_spindle_speed(self) -> Optional[int]:
        """Read current spindle speed in RPM."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            if self.fwlib and self.handle:
                speed = ctypes.c_long()
                ret = self.fwlib.cnc_rdspeed(self.handle, 0, ctypes.byref(speed))
                if ret == 0:
                    return speed.value
            else:
                # Simulation mode
                import random
                return random.randint(0, 12000)
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading spindle speed: {e}")
        
        return None
    
    def read_feed_rate(self) -> Optional[float]:
        """Read current feed rate in mm/min."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            if self.fwlib and self.handle:
                feed = ctypes.c_long()
                ret = self.fwlib.cnc_actf(self.handle, ctypes.byref(feed))
                if ret == 0:
                    return feed.value / 100.0  # Convert to mm/min
            else:
                # Simulation mode
                import random
                return random.uniform(0, 5000)
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading feed rate: {e}")
        
        return None
    
    def read_operation_mode(self) -> Optional[FanucMode]:
        """Read current operation mode."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            if self.fwlib and self.handle:
                mode = ctypes.c_short()
                ret = self.fwlib.cnc_statmode(self.handle, ctypes.byref(mode))
                if ret == 0:
                    return FanucMode(mode.value)
            else:
                # Simulation mode
                return FanucMode.AUTO
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading operation mode: {e}")
        
        return None
    
    def read_alarms(self) -> Optional[List[Dict[str, Any]]]:
        """Read active alarms."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            alarms = []
            if self.fwlib and self.handle:
                # FOCAS alarm reading
                alarm_info = ctypes.create_string_buffer(256)
                ret = self.fwlib.cnc_rdalmmsg(self.handle, 0, alarm_info)
                if ret == 0:
                    msg = alarm_info.value.decode('ascii', errors='ignore')
                    alarms.append({
                        'number': 0,
                        'message': msg,
                        'timestamp': datetime.now().isoformat()
                    })
            else:
                # Simulation mode - return empty
                pass
                
            return alarms if alarms else None
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading alarms: {e}")
        
        return None
    
    def read_tool_info(self) -> Optional[Dict[str, Any]]:
        """Read current tool information."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            if self.fwlib and self.handle:
                tool_num = ctypes.c_long()
                ret = self.fwlib.cnc_toolnum(self.handle, 0, ctypes.byref(tool_num))
                if ret == 0:
                    return {
                        'tool_number': tool_num.value,
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                # Simulation mode
                import random
                return {
                    'tool_number': random.randint(1, 20),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading tool info: {e}")
        
        return None
    
    def read_program_name(self) -> Optional[str]:
        """Read current program name."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            if self.fwlib and self.handle:
                prog_name = ctypes.create_string_buffer(32)
                ret = self.fwlib.cnc_rdprgname(self.handle, prog_name)
                if ret == 0:
                    return prog_name.value.decode('ascii', errors='ignore').strip()
            else:
                # Simulation mode
                return "O0001"
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading program name: {e}")
        
        return None
    
    def read_machine_status(self) -> Optional[Dict[str, Any]]:
        """Read comprehensive machine status."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            status = {
                'ip': self.ip,
                'connected': True,
                'timestamp': datetime.now().isoformat(),
                'axes': self.read_all_axes(),
                'spindle_speed': self.read_spindle_speed(),
                'feed_rate': self.read_feed_rate(),
                'operation_mode': self.read_operation_mode().name if self.read_operation_mode() else None,
                'program_name': self.read_program_name(),
                'tool_info': self.read_tool_info(),
                'alarms': self.read_alarms()
            }
            return status
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading machine status: {e}")
        
        return None
    
    def write_macro_variable(self, number: int, value: float) -> bool:
        """
        Write to a macro variable.
        
        Args:
            number: Macro variable number
            value: Value to write
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            if self.fwlib and self.handle:
                val = ctypes.c_double(value)
                ret = self.fwlib.cnc_wrmacro(self.handle, number, ctypes.byref(val))
                return ret == 0
            else:
                # Simulation mode
                logger.debug(f"Simulation: Write macro {number} = {value}")
                return True
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error writing macro variable: {e}")
        
        return False
    
    def read_macro_variable(self, number: int) -> Optional[float]:
        """
        Read a macro variable.
        
        Args:
            number: Macro variable number
            
        Returns:
            Variable value or None on error
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            if self.fwlib and self.handle:
                val = ctypes.c_double()
                ret = self.fwlib.cnc_rdmacro(self.handle, number, ctypes.byref(val))
                if ret == 0:
                    return val.value
            else:
                # Simulation mode
                import random
                return random.uniform(0, 1000)
                
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading macro variable: {e}")
        
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
