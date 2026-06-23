"""
Tests for Audit Trails Module
"""
import pytest
import os
import json
import shutil
from datetime import datetime, timedelta
from audit_trails import AuditTrail, AuditEventType

@pytest.fixture
def temp_audit_trail():
    test_dir = "./test_audit_logs"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    trail = AuditTrail()
    trail.log_dir = test_dir
    os.makedirs(test_dir, exist_ok=True)
    trail.buffer_size = 1  # Flush immediately

    yield trail

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def test_log_event(temp_audit_trail):
    event_id = temp_audit_trail.log(
        event_type=AuditEventType.LOGIN,
        user_id="test_user",
        resource_type="auth",
        status="SUCCESS"
    )
    assert event_id is not None

    # Check if file exists
    files = os.listdir(temp_audit_trail.log_dir)
    assert len(files) > 0

def test_query_events(temp_audit_trail):
    temp_audit_trail.log(AuditEventType.LOGIN, "user1", "auth")
    temp_audit_trail.log(AuditEventType.DATA_READ, "user1", "machine")
    temp_audit_trail.log(AuditEventType.LOGIN, "user2", "auth")

    results = temp_audit_trail.query(user_id="user1")
    assert len(results) == 2

    results = temp_audit_trail.query(event_type=AuditEventType.LOGIN)
    assert len(results) == 2

def test_integrity_verification(temp_audit_trail):
    temp_audit_trail.log(AuditEventType.CONFIG_CHANGED, "admin", "system")
    results = temp_audit_trail.query()
    assert len(results) == 1
    event = results[0]
    assert temp_audit_trail._verify_checksum(event) == True

    # Tamper with data
    event["user_id"] = "hacker"
    assert temp_audit_trail._verify_checksum(event) == False

def test_compliance_report(temp_audit_trail):
    temp_audit_trail.log(AuditEventType.LOGIN, "user1", "auth")
    temp_audit_trail.log(AuditEventType.LOGIN_FAILED, "user1", "auth", status="FAILURE")

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow() + timedelta(days=1)

    report = temp_audit_trail.generate_compliance_report(start, end)
    assert report["statistics"]["total_events"] == 2
    assert report["statistics"]["by_status"]["FAILURE"] == 1
