"""
Fanuc FOCAS Connector for OMAYA
Interface for Fanuc CNC machines
"""
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class FanucMode(Enum):
    AUTO = 0
    EDIT = 1
    MDI = 2
    HANDLE = 3
    JOG = 4

class FanucAxis(Enum):
    X = 0
    Y = 1
    Z = 2
    A = 3
    B = 4
    C = 5

class FanucConnector:
    """Fanuc FOCAS 1/2 Protocol Connector"""
    
    def __init__(self, ip: str, port: int = 8193, timeout: int = 10):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.connected = False
        self.handle = None
        self.fwlib = None
        self.last_error = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self) -> bool:
        """Simulated connection to Fanuc CNC"""
        logger.info(f"Connecting to Fanuc CNC at {self.ip}:{self.port}")
        self.connected = True
        return True

    def disconnect(self) -> bool:
        """Disconnect from CNC"""
        if self.fwlib and self.handle:
            self.fwlib.cnc_freelibhndl(self.handle)
        self.connected = False
        self.handle = None
        logger.info("Disconnected from Fanuc CNC")
        return True

    def get_last_error(self) -> str:
        return self.last_error

    def read_axis_position(self, axis: FanucAxis) -> float:
        """Read absolute position for a given axis"""
        if not self.connected:
            return 0.0
        
        if not self.fwlib:
            # Simulation mode
            return 123.456
        
        class Ref:
            def __init__(self): self._obj = type('obj', (), {'value': 0.0})()

        pos_ref = Ref()
        rc = self.fwlib.cnc_absolute(self.handle, axis.value, pos_ref)
        return pos_ref._obj.value if rc == 0 else 0.0

    def read_all_axes(self) -> Dict[str, float]:
        """Read positions of all principal axes"""
        return {
            "X": self.read_axis_position(FanucAxis.X),
            "Y": self.read_axis_position(FanucAxis.Y),
            "Z": self.read_axis_position(FanucAxis.Z)
        }

    def read_spindle_speed(self) -> int:
        """Read current spindle speed"""
        if not self.connected:
            return 0
        
        if not self.fwlib:
            return 1500

        class Ref:
            def __init__(self): self._obj = type('obj', (), {'value': 0})()

        speed_ref = Ref()
        rc = self.fwlib.cnc_rdspeed(self.handle, 1, speed_ref)
        return int(speed_ref._obj.value) if rc == 0 else 0

    def read_feed_rate(self) -> float:
        """Read current feed rate"""
        if not self.connected:
            return 0.0

        if not self.fwlib:
            return 250.0

        class Ref:
            def __init__(self): self._obj = type('obj', (), {'value': 0})()

        feed_ref = Ref()
        rc = self.fwlib.cnc_actf(self.handle, feed_ref)
        return float(feed_ref._obj.value) / 100.0 if rc == 0 else 0.0

    def read_operation_mode(self) -> FanucMode:
        """Read current operation mode"""
        if not self.connected:
            return FanucMode.JOG

        if not self.fwlib:
            return FanucMode.AUTO

        class Ref:
            def __init__(self): self._obj = type('obj', (), {'value': 0})()

        mode_ref = Ref()
        rc = self.fwlib.cnc_statmode(self.handle, mode_ref)
        try:
            return FanucMode(mode_ref._obj.value) if rc == 0 else FanucMode.JOG
        except ValueError:
            return FanucMode.JOG

    def read_alarms(self) -> Optional[List[Dict[str, Any]]]:
        """Read current machine alarms"""
        if not self.connected:
            return None
        return [] # Simulation: no alarms

    def read_tool_info(self) -> Dict[str, Any]:
        """Read current tool information"""
        if not self.connected:
            return {}
        return {"tool_number": 1, "tool_life": 85}

    def read_program_name(self) -> str:
        """Read current active program name"""
        if not self.connected:
            return ""
        return "O1234.NC"

    def write_macro_variable(self, number: int, value: float) -> bool:
        """Write value to CNC macro variable"""
        if not self.connected:
            return False
            
        if not self.fwlib:
            return True

        class Ref:
            def __init__(self): self._obj = type('obj', (), {'value': value})()
            
        val_ref = Ref()
        rc = self.fwlib.cnc_wrmacro(self.handle, number, val_ref)
        return rc == 0

    def read_macro_variable(self, number: int) -> float:
        """Read value from CNC macro variable"""
        if not self.connected:
            return 0.0
            
        if not self.fwlib:
            return 99.9

        class Ref:
            def __init__(self): self._obj = type('obj', (), {'value': 0.0})()

        val_ref = Ref()
        rc = self.fwlib.cnc_rdmacro(self.handle, number, val_ref)
        return val_ref._obj.value if rc == 0 else 0.0

    def read_machine_status(self) -> Dict[str, Any]:
        """Comprehensive status read"""
        return {
            "ip": self.ip,
            "connected": self.connected,
            "axes": self.read_all_axes(),
            "spindle_speed": self.read_spindle_speed(),
            "feed_rate": self.read_feed_rate(),
            "mode": self.read_operation_mode().name
        }
