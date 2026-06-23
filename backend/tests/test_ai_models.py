import pytest
from ai_models import LSTMPredictor, RULPredictor, AnomalyDetector

def test_lstm_predictor():
    predictor = LSTMPredictor()
    features = {
        "temperature": 80.0,
        "vibration": 3.5,
        "toolWear": 90,
        "operatingHours": 5000
    }

    prediction = predictor.predict_failure(features)

    assert "failureProbability" in prediction
    assert prediction["failureProbability"] >= 0.0
    assert prediction["failureProbability"] <= 1.0
    assert len(prediction["factors"]) > 0
    # Higher features should lead to higher probability (due to mock logic)
    assert prediction["failureProbability"] > 0.5

def test_rul_predictor():
    predictor = RULPredictor()
    features = {
        "temperature": 75.0,
        "vibration": 2.5,
        "toolWear": 80
    }

    prediction = predictor.predict_rul(features)

    assert "rul_hours" in prediction
    assert prediction["rul_hours"] > 0
    assert "confidence_interval" in prediction
    assert "recommended_action" in prediction

def test_anomaly_detector():
    detector = AnomalyDetector()

    # Normal features
    normal_features = {
        "temperature": 60.0,
        "vibration": 1.5,
        "spindleSpeed": 10000,
        "toolWear": 50
    }
    result = detector.detect_anomaly("M1", normal_features)
    assert result["isAnomalous"] is False

    # Anomalous features
    anomalous_features = {
        "temperature": 95.0, # High
        "vibration": 4.0,  # High
        "spindleSpeed": 10000,
        "toolWear": 50
    }
    result = detector.detect_anomaly("M1", anomalous_features)
    assert result["isAnomalous"] is True
    assert len(result["anomalies"]) >= 2
