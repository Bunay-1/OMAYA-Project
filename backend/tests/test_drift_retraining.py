"""
Tests for Model Drift Detection and Retraining
"""
import pytest
import numpy as np
from backend.drift_detection import DriftDetector
from unittest.mock import patch, MagicMock

def test_drift_detection_and_retraining_trigger():
    detector = DriftDetector(window_size=200)

    # Add normal data (baseline)
    for i in range(100):
        detector.add_prediction(0.1, 0.1, {"temp": 50.0 + i % 5})

    # Add drifted data
    for i in range(100):
        detector.add_prediction(0.1, 0.1, {"temp": 80.0 + i % 5})

    # Check if drift is detected and retraining triggered
    with patch('backend.drift_detection.logger') as mock_logger:
        import audit_trails
        with patch.object(audit_trails.audit_trail, 'log') as mock_log:
            result = detector.detect_drift()

            assert bool(result["hasDrift"]) is True
            assert bool(result["featureDrift"]) is True
            assert result["maxPSI"] > 0.2
            assert result["retrainingTriggered"] is True

            # Verify logging
            mock_logger.warning.assert_called()
            mock_log.assert_called_once()
            args, kwargs = mock_log.call_args
            assert kwargs["event_type"] == audit_trails.AuditEventType.MODEL_TRAINED

def test_no_drift_no_retraining():
    detector = DriftDetector(window_size=200)

    # Add consistent data
    for i in range(200):
        detector.add_prediction(0.1, 0.1, {"temp": 50.0 + i % 5})

    result = detector.detect_drift()
    assert bool(result["hasDrift"]) is False
    assert result["retrainingTriggered"] is False
