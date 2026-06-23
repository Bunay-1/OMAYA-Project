import pytest
from kafka_streams import RealTimeAggregator, AlertAggregator, PredictionTracker
from datetime import datetime, timedelta

def test_real_time_aggregator_logic():
    agg = RealTimeAggregator(window_size_seconds=60)
    machine_id = "M1"

    # Add multiple data points
    now = datetime.now()
    for i in range(5):
        event = {
            "machine_id": machine_id,
            "timestamp": (now + timedelta(seconds=i)).isoformat(),
            "data": {"temperature": 60 + i * 2, "vibration": 1.0}
        }
        agg.add_telemetry(event)

    metrics = agg.get_metrics(machine_id)
    assert metrics["sample_count"] == 5
    # Avg temp: (60+62+64+66+68)/5 = 64
    assert metrics["temperature"]["avg"] == 64.0

def test_alert_aggregator_limit():
    agg = AlertAggregator()
    machine_id = "M1"

    # Add 120 alerts (limit is 100 per machine)
    for i in range(120):
        event = {
            "machine_id": machine_id,
            "id": f"alert-{i}",
            "severity": "warning",
            "title": f"Alert {i}"
        }
        agg.add_alert(event)

    alerts = agg.get_alerts_by_machine(machine_id)
    assert len(alerts) == 100
    # Should be the LATEST 100 alerts
    assert alerts[0]["id"] == "alert-20"

def test_prediction_tracker():
    tracker = PredictionTracker()
    machine_id = "M1"

    # Add failure prediction
    tracker.add_prediction({
        "machine_id": machine_id,
        "prediction_type": "failure",
        "data": {"failureProbability": 0.3}
    })

    # Add RUL prediction
    tracker.add_prediction({
        "machine_id": machine_id,
        "prediction_type": "rul",
        "data": {"rul_hours": 150}
    })

    assert tracker.get_latest_prediction(machine_id, "failure")["data"]["failureProbability"] == 0.3
    assert len(tracker.get_predictions(machine_id)) == 2
