import pytest
from drift_detection import DriftDetector
from online_learning import OnlineAnomalyDetector
from explainable_ai import ExplainableAI
import numpy as np

def test_drift_detector():
    detector = DriftDetector()

    # Add some initial stable data
    for _ in range(10):
        detector.add_prediction(0.2, 0, {"temp": 60})

    status = detector.detect_drift()
    assert status["hasDrift"] is False

    # Simulate drift
    for _ in range(20):
        detector.add_prediction(0.8, 0, {"temp": 90})

    status = detector.detect_drift()
    assert "hasDrift" in status

def test_online_anomaly_detector():
    detector = OnlineAnomalyDetector(window_size=50)

    # Not trained yet
    data = {"temperature": 60, "vibration": 1.0, "spindleSpeed": 10000}
    res = detector.predict(data)
    assert bool(res["isAnomalous"]) is False
    assert "training" in res["reason"]

    # Train it
    for i in range(25):
        detector.update({"temperature": 60 + i%2, "vibration": 1.0, "spindleSpeed": 10000})

    assert detector.trained is True

    # Normal prediction
    res = detector.predict({"temperature": 60, "vibration": 1.0, "spindleSpeed": 10000})
    assert bool(res["isAnomalous"]) is False

    # Anomaly prediction
    res = detector.predict({"temperature": 100, "vibration": 5.0, "spindleSpeed": 15000})
    assert bool(res["isAnomalous"]) is True

def test_explainable_ai():
    xai = ExplainableAI()
    features = {"temp": 70, "wear": 80}

    # Test SHAP mock
    shap_vals = xai._mock_shap_explanation(features)
    assert "contributions" in shap_vals

    # Test LIME mock
    lime_vals = xai._mock_lime_explanation(features)
    assert "prediction_probability" in lime_vals
    assert "contributions" in lime_vals
