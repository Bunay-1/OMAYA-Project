"""
Audit Trails Module
Compliance logging and activity tracking
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib
import uuid

logger = logging.getLogger(__name__)

class AuditEventType(str, Enum):
    """Types of audit events"""
    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    TOKEN_REFRESH = "TOKEN_REFRESH"
    
    # Data Access
    DATA_READ = "DATA_READ"
    DATA_CREATE = "DATA_CREATE"
    DATA_UPDATE = "DATA_UPDATE"
    DATA_DELETE = "DATA_DELETE"
    DATA_EXPORT = "DATA_EXPORT"
    
    # Alerts
    ALERT_CREATED = "ALERT_CREATED"
    ALERT_ACKNOWLEDGED = "ALERT_ACKNOWLEDGED"
    ALERT_ESCALATED = "ALERT_ESCALATED"
    ALERT_RESOLVED = "ALERT_RESOLVED"
    
    # Maintenance
    MAINTENANCE_SCHEDULED = "MAINTENANCE_SCHEDULED"
    MAINTENANCE_COMPLETED = "MAINTENANCE_COMPLETED"
    MAINTENANCE_CANCELLED = "MAINTENANCE_CANCELLED"
    
    # AI/Predictions
    PREDICTION_REQUESTED = "PREDICTION_REQUESTED"
    MODEL_TRAINED = "MODEL_TRAINED"
    MODEL_DEPLOYED = "MODEL_DEPLOYED"
    
    # System
    CONFIG_CHANGED = "CONFIG_CHANGED"
    USER_CREATED = "USER_CREATED"
    USER_MODIFIED = "USER_MODIFIED"
    PERMISSION_CHANGED = "PERMISSION_CHANGED"

class AuditTrail:
    """
    Audit trail logger for compliance and security
    """
    
    def __init__(self):
        self.storage_backend = os.getenv("AUDIT_STORAGE", "file")  # file, database, s3
        self.log_dir = os.getenv("AUDIT_LOG_DIR", "./audit_logs")
        self.retention_days = int(os.getenv("AUDIT_RETENTION_DAYS", "365"))
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # In-memory buffer for batch writing
        self.buffer: List[Dict] = []
        self.buffer_size = int(os.getenv("AUDIT_BUFFER_SIZE", "100"))
    
    def log(
        self,
        event_type: AuditEventType,
        user_id: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        action_details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None
    ) -> str:
        """
        Log an audit event
        
        Args:
            event_type: Type of event
            user_id: User who performed the action
            resource_type: Type of resource accessed
            resource_id: ID of the resource
            action_details: Additional details
            ip_address: Client IP address
            user_agent: Client user agent
            status: SUCCESS or FAILURE
            error_message: Error message if failed
            
        Returns:
            Audit event ID
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        audit_event = {
            "event_id": event_id,
            "timestamp": timestamp.isoformat() + "Z",
            "event_type": event_type.value,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action_details": action_details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": status,
            "error_message": error_message,
            "checksum": None  # Will be calculated
        }
        
        # Calculate checksum for integrity
        audit_event["checksum"] = self._calculate_checksum(audit_event)
        
        # Add to buffer
        self.buffer.append(audit_event)
        
        # Write if buffer is full
        if len(self.buffer) >= self.buffer_size:
            self._flush_buffer()
        
        logger.info(
            f"Audit: {event_type.value} by {user_id} on {resource_type}"
            f"{'/' + resource_id if resource_id else ''} - {status}"
        )
        
        return event_id
    
    def _calculate_checksum(self, event: Dict) -> str:
        """Calculate SHA-256 checksum for event integrity"""
        # Create a copy without checksum field
        event_copy = {k: v for k, v in event.items() if k != "checksum"}
        event_str = json.dumps(event_copy, sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    def _verify_checksum(self, event: Dict) -> bool:
        """Verify event integrity using checksum"""
        stored_checksum = event.get("checksum")
        calculated_checksum = self._calculate_checksum(event)
        return stored_checksum == calculated_checksum
    
    def _flush_buffer(self):
        """Flush buffer to storage"""
        if not self.buffer:
            return
        
        if self.storage_backend == "file":
            self._write_to_file()
        elif self.storage_backend == "database":
            self._write_to_database()
        elif self.storage_backend == "s3":
            self._write_to_s3()
        
        self.buffer.clear()
    
    def _write_to_file(self):
        """Write audit events to log files"""
        timestamp = datetime.utcnow()
        filename = f"{self.log_dir}/audit_{timestamp.strftime('%Y%m%d')}.jsonl"
        
        try:
            with open(filename, "a") as f:
                for event in self.buffer:
                    f.write(json.dumps(event) + "\n")
            logger.debug(f"Wrote {len(self.buffer)} audit events to {filename}")
        except Exception as e:
            logger.error(f"Error writing audit log: {e}")
    
    def _write_to_database(self):
        """Write audit events to database"""
        # Placeholder for database implementation
        logger.debug(f"Would write {len(self.buffer)} events to database")
    
    def _write_to_s3(self):
        """Write audit events to S3/MinIO"""
        try:
            from data_lake import data_lake
            
            for event in self.buffer:
                data_lake.store_telemetry("audit", event)
        except Exception as e:
            logger.error(f"Error writing audit to S3: {e}")
    
    def query(
        self,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query audit events
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user
            resource_type: Filter by resource type
            start_date: Filter from date
            end_date: Filter to date
            limit: Maximum results
            
        Returns:
            List of matching audit events
        """
        # Flush buffer first
        self._flush_buffer()
        
        results = []
        
        # Read from file storage
        if self.storage_backend == "file":
            results = self._query_files(
                event_type, user_id, resource_type,
                start_date, end_date, limit
            )
        
        return results
    
    def _query_files(
        self,
        event_type: Optional[AuditEventType],
        user_id: Optional[str],
        resource_type: Optional[str],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        limit: int
    ) -> List[Dict]:
        """Query audit events from files"""
        results = []
        
        try:
            import glob
            
            files = sorted(
                glob.glob(f"{self.log_dir}/audit_*.jsonl"),
                reverse=True
            )
            
            for filepath in files:
                with open(filepath, "r") as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            
                            # Apply filters
                            if event_type and event["event_type"] != event_type.value:
                                continue
                            if user_id and event["user_id"] != user_id:
                                continue
                            if resource_type and event["resource_type"] != resource_type:
                                continue
                            
                            event_time = datetime.fromisoformat(
                                event["timestamp"].replace("Z", "+00:00")
                            ).replace(tzinfo=None)
                            
                            if start_date and event_time < start_date:
                                continue
                            if end_date and event_time > end_date:
                                continue
                            
                            # Verify integrity
                            if self._verify_checksum(event):
                                results.append(event)
                            else:
                                logger.warning(f"Integrity check failed for event {event['event_id']}")
                            
                            if len(results) >= limit:
                                return results
                                
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Error querying audit files: {e}")
        
        return results
    
    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "summary"
    ) -> Dict:
        """
        Generate compliance report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            report_type: summary, detailed, or full
            
        Returns:
            Compliance report
        """
        events = self.query(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Aggregate statistics
        stats = {
            "total_events": len(events),
            "by_event_type": {},
            "by_user": {},
            "by_status": {"SUCCESS": 0, "FAILURE": 0},
            "by_resource_type": {},
            "security_events": [],
            "failed_events": []
        }
        
        for event in events:
            # By event type
            et = event["event_type"]
            stats["by_event_type"][et] = stats["by_event_type"].get(et, 0) + 1
            
            # By user
            uid = event["user_id"]
            stats["by_user"][uid] = stats["by_user"].get(uid, 0) + 1
            
            # By status
            status = event["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # By resource type
            rt = event["resource_type"]
            stats["by_resource_type"][rt] = stats["by_resource_type"].get(rt, 0) + 1
            
            # Track security events
            if et in ["LOGIN_FAILED", "PERMISSION_CHANGED", "USER_CREATED"]:
                stats["security_events"].append(event)
            
            # Track failures
            if status == "FAILURE":
                stats["failed_events"].append(event)
        
        return {
            "report_type": report_type,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "statistics": stats,
            "integrity_verified": True
        }
    
    def close(self):
        """Flush remaining events and close"""
        self._flush_buffer()
        logger.info("Audit trail closed")

# Singleton instance
audit_trail = AuditTrail()

# Convenience functions
def log_login(user_id: str, ip_address: str, success: bool = True):
    """Log login event"""
    audit_trail.log(
        event_type=AuditEventType.LOGIN if success else AuditEventType.LOGIN_FAILED,
        user_id=user_id,
        resource_type="authentication",
        ip_address=ip_address,
        status="SUCCESS" if success else "FAILURE"
    )

def log_data_access(user_id: str, resource_type: str, resource_id: str, action: str = "read"):
    """Log data access event"""
    event_map = {
        "read": AuditEventType.DATA_READ,
        "create": AuditEventType.DATA_CREATE,
        "update": AuditEventType.DATA_UPDATE,
        "delete": AuditEventType.DATA_DELETE,
        "export": AuditEventType.DATA_EXPORT
    }
    
    audit_trail.log(
        event_type=event_map.get(action, AuditEventType.DATA_READ),
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id
    )

def log_alert_action(user_id: str, alert_id: str, action: str):
    """Log alert-related action"""
    event_map = {
        "create": AuditEventType.ALERT_CREATED,
        "acknowledge": AuditEventType.ALERT_ACKNOWLEDGED,
        "escalate": AuditEventType.ALERT_ESCALATED,
        "resolve": AuditEventType.ALERT_RESOLVED
    }
    
    audit_trail.log(
        event_type=event_map.get(action, AuditEventType.ALERT_CREATED),
        user_id=user_id,
        resource_type="alert",
        resource_id=alert_id
    )
