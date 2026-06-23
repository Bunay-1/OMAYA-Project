"""
Kafka Streams Processing
Real-time analytics and aggregations on machine events
"""

import json
from typing import Dict, Any
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class RealTimeAggregator:
    """
    Aggregates machine events in real-time
    Maintains windows of data for analytics
    """
    
    def __init__(self, window_size_seconds: int = 300):
        """
        Initialize aggregator
        
        Args:
            window_size_seconds: Size of aggregation window (default 5 minutes)
        """
        self.window_size = timedelta(seconds=window_size_seconds)
        self.data_windows = defaultdict(list)  # machine_id -> [events]
        self.metrics = defaultdict(dict)  # machine_id -> metrics
    
    def add_telemetry(self, event: Dict[str, Any]):
        """Add telemetry event to aggregation window"""
        machine_id = event.get("machine_id")
        timestamp = datetime.fromisoformat(event.get("timestamp", datetime.now().isoformat()))
        
        # Clean old events
        self._clean_old_events(machine_id, timestamp)
        
        # Add new event
        self.data_windows[machine_id].append({
            "timestamp": timestamp,
            "data": event.get("data", {})
        })
        
        # Update metrics
        self._update_metrics(machine_id)
    
    def _clean_old_events(self, machine_id: str, current_time: datetime):
        """Remove events older than window size"""
        cutoff_time = current_time - self.window_size
        
        if machine_id in self.data_windows:
            self.data_windows[machine_id] = [
                event for event in self.data_windows[machine_id]
                if event["timestamp"] > cutoff_time
            ]
    
    def _update_metrics(self, machine_id: str):
        """Calculate metrics for current window"""
        if not self.data_windows.get(machine_id):
            return
        
        events = self.data_windows[machine_id]
        temperatures = [e["data"].get("temperature") for e in events if e["data"].get("temperature")]
        vibrations = [e["data"].get("vibration") for e in events if e["data"].get("vibration")]
        speeds = [e["data"].get("spindleSpeed") for e in events if e["data"].get("spindleSpeed")]
        
        metrics = {
            "sample_count": len(events),
            "time_window_minutes": (self.window_size.total_seconds() / 60),
            "temperature": {},
            "vibration": {},
            "spindleSpeed": {}
        }
        
        if temperatures:
            metrics["temperature"] = {
                "avg": sum(temperatures) / len(temperatures),
                "min": min(temperatures),
                "max": max(temperatures)
            }
        
        if vibrations:
            metrics["vibration"] = {
                "avg": sum(vibrations) / len(vibrations),
                "min": min(vibrations),
                "max": max(vibrations)
            }
        
        if speeds:
            metrics["spindleSpeed"] = {
                "avg": sum(speeds) / len(speeds),
                "min": min(speeds),
                "max": max(speeds)
            }
        
        self.metrics[machine_id] = metrics
    
    def get_metrics(self, machine_id: str = None) -> Dict:
        """
        Get aggregated metrics
        
        Args:
            machine_id: Specific machine or None for all
            
        Returns:
            Dict with metrics
        """
        if machine_id:
            return self.metrics.get(machine_id, {})
        return dict(self.metrics)


class AlertAggregator:
    """Aggregates alerts by severity and machine"""
    
    def __init__(self):
        self.alerts_by_machine = defaultdict(list)  # machine_id -> [alerts]
        self.alerts_by_severity = defaultdict(list)  # severity -> [alerts]
    
    def add_alert(self, event: Dict[str, Any]):
        """Add alert event"""
        machine_id = event.get("machine_id")
        severity = event.get("severity", "info")
        
        alert = {
            "id": event.get("id", f"alert-{datetime.now().timestamp()}"),
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "severity": severity,
            "title": event.get("title"),
            "message": event.get("message"),
            "metadata": event.get("metadata", {})
        }
        
        self.alerts_by_machine[machine_id].append(alert)
        self.alerts_by_severity[severity].append(alert)
        
        # Keep only last 100 alerts per machine
        if len(self.alerts_by_machine[machine_id]) > 100:
            removed = self.alerts_by_machine[machine_id].pop(0)
            self.alerts_by_severity[removed["severity"]].remove(removed)
    
    def get_alerts_by_machine(self, machine_id: str) -> list:
        """Get alerts for specific machine"""
        return self.alerts_by_machine.get(machine_id, [])
    
    def get_alerts_by_severity(self, severity: str = None) -> Dict:
        """Get alerts by severity"""
        if severity:
            return {severity: self.alerts_by_severity.get(severity, [])}
        return dict(self.alerts_by_severity)
    
    def get_active_critical_alerts(self) -> list:
        """Get all active critical alerts"""
        return self.alerts_by_severity.get("critical", [])


class PredictionTracker:
    """Tracks AI predictions over time"""
    
    def __init__(self):
        self.predictions = defaultdict(list)  # machine_id -> [predictions]
        self.latest = {}  # machine_id -> latest prediction
    
    def add_prediction(self, event: Dict[str, Any]):
        """Add prediction event"""
        machine_id = event.get("machine_id")
        prediction_type = event.get("prediction_type")
        
        prediction = {
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "type": prediction_type,
            "data": event.get("data", {})
        }
        
        self.predictions[machine_id].append(prediction)
        
        # Store latest prediction by type
        key = f"{machine_id}:{prediction_type}"
        self.latest[key] = prediction
        
        # Keep only last 1000 predictions per machine
        if len(self.predictions[machine_id]) > 1000:
            self.predictions[machine_id].pop(0)
    
    def get_predictions(self, machine_id: str) -> list:
        """Get all predictions for machine"""
        return self.predictions.get(machine_id, [])
    
    def get_latest_prediction(self, machine_id: str, prediction_type: str = None):
        """Get latest prediction"""
        if prediction_type:
            key = f"{machine_id}:{prediction_type}"
            return self.latest.get(key)
        
        # Return latest prediction of any type
        predictions = self.predictions.get(machine_id, [])
        return predictions[-1] if predictions else None
    
    def get_failure_trend(self, machine_id: str, limit: int = 10) -> list:
        """Get failure probability trend"""
        predictions = self.predictions.get(machine_id, [])
        failure_preds = [
            p for p in predictions
            if p["type"] == "failure"
        ]
        return failure_preds[-limit:]
    
    def get_rul_trend(self, machine_id: str, limit: int = 10) -> list:
        """Get RUL trend over time"""
        predictions = self.predictions.get(machine_id, [])
        rul_preds = [
            p for p in predictions
            if p["type"] == "rul"
        ]
        return rul_preds[-limit:]


# Global aggregator instances
telemetry_aggregator = RealTimeAggregator(window_size_seconds=300)  # 5 minutes
alert_aggregator = AlertAggregator()
prediction_tracker = PredictionTracker()


def process_telemetry_event(event: Dict[str, Any]):
    """Process telemetry event"""
    try:
        telemetry_aggregator.add_telemetry(event)
    except Exception as e:
        logger.error(f"Error processing telemetry event: {e}")


def process_alert_event(event: Dict[str, Any]):
    """Process alert event"""
    try:
        alert_aggregator.add_alert(event)
    except Exception as e:
        logger.error(f"Error processing alert event: {e}")


def process_prediction_event(event: Dict[str, Any]):
    """Process prediction event"""
    try:
        prediction_tracker.add_prediction(event)
    except Exception as e:
        logger.error(f"Error processing prediction event: {e}")
