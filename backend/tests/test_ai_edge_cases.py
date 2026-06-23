import pytest
from ai_models import LSTMPredictor, RULPredictor, AnomalyDetector

def test_lstm_invalid_features():
    predictor = LSTMPredictor()
    # Test with empty features
    res = predictor.predict_failure({})
    assert "failureProbability" in res

    # Test with extreme values - mock logic adds noise, so we check for high prob
    res = predictor.predict_failure({"temperature": 1000, "vibration": 100})
    assert res["failureProbability"] > 0.4

def test_rul_invalid_features():
    predictor = RULPredictor()
    # Test with extreme values
    res = predictor.predict_rul({"temperature": 500})
    assert res["rul_hours"] < 500 # Should be low

def test_anomaly_missing_features():
    detector = AnomalyDetector()
    # Should not crash with missing features
    res = detector.detect_anomaly("M1", {})
    assert res["isAnomalous"] is False

def test_anomaly_boundary_values():
    detector = AnomalyDetector()
    # Exactly on threshold
    res = detector.detect_anomaly("M1", {"temperature": 80.0})
    assert res["isAnomalous"] is False

    # High score
    res = detector.detect_anomaly("M1", {"temperature": 200, "vibration": 10, "toolWear": 200})
    assert res["isAnomalous"] is True
