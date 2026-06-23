import pytest
import os
import json
from audit_trails import log_login, log_data_access, log_alert_action, audit_trail, AuditEventType

def test_log_login_helper():
    audit_trail.buffer.clear()
    log_login("user123", "127.0.0.1", True)
    assert len(audit_trail.buffer) == 1
    assert audit_trail.buffer[0]["event_type"] == AuditEventType.LOGIN
    assert audit_trail.buffer[0]["user_id"] == "user123"

def test_log_data_access_helper():
    audit_trail.buffer.clear()
    log_data_access("admin", "machine_telemetry", "M1", "read")
    assert len(audit_trail.buffer) == 1
    assert audit_trail.buffer[0]["event_type"] == AuditEventType.DATA_READ

def test_log_alert_action_helper():
    audit_trail.buffer.clear()
    log_alert_action("operator1", "A-555", "acknowledge")
    assert len(audit_trail.buffer) == 1
    assert audit_trail.buffer[0]["event_type"] == AuditEventType.ALERT_ACKNOWLEDGED

def test_audit_trail_integrity_fail():
    event = {
        "event_id": "123",
        "timestamp": "2024-01-01T00:00:00Z",
        "user_id": "admin",
        "checksum": "wrong"
    }
    assert audit_trail._verify_checksum(event) is False
