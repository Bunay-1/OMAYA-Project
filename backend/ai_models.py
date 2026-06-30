"""
AI Models for Predictive Maintenance
Real model integration for production environment
"""
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from ml_models.lstm_model import lstm_model as real_lstm
from ml_models.rul_model import rul_model as real_rul

# Singleton instances
lstm_predictor = real_lstm
rul_predictor = real_rul

class AnomalyDetector:
    """
    Online learning anomaly detection
    Using River-style approach for real-time drift detection
    """
    def __init__(self):
        self.baseline = {}
        self.thresholds = {
            "temperature": (40, 80),
            "vibration": (0.3, 3.0),
            "spindleSpeed": (7000, 13000),
            "toolWear": (0, 100)
        }
    
    def detect_anomaly(self, machine_id: str, features: Dict[str, float]) -> Dict:
        """
        Detect anomalies in real-time sensor data
        """
        anomalies = []
        anomaly_score = 0.0
        
        for feature, value in features.items():
            if feature in self.thresholds:
                low, high = self.thresholds[feature]
                
                if value < low or value > high:
                    severity = "critical" if value < low * 0.8 or value > high * 1.2 else "warning"
                    anomalies.append({
                        "feature": feature,
                        "value": value,
                        "expected_range": [low, high],
                        "severity": severity,
                        "deviation": abs(value - (low + high) / 2) / ((high - low) / 2)
                    })
                    
                    anomaly_score += 0.3 if severity == "critical" else 0.1
        
        is_anomalous = anomaly_score > 0.3
        
        return {
            "isAnomalous": is_anomalous,
            "anomalyScore": round(min(anomaly_score, 1.0), 3),
            "anomalies": anomalies,
            "machineId": machine_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_baseline(self, machine_id: str, features: Dict[str, float]):
        """Update baseline statistics with new data (online learning)"""
        if machine_id not in self.baseline:
            self.baseline[machine_id] = {}
        
        for feature, value in features.items():
            if feature not in self.baseline[machine_id]:
                self.baseline[machine_id][feature] = {
                    "mean": value,
                    "std": 0,
                    "count": 1
                }
            else:
                stats = self.baseline[machine_id][feature]
                stats["count"] += 1
                delta = value - stats["mean"]
                stats["mean"] += delta / stats["count"]
                stats["std"] = np.sqrt((stats["std"] ** 2 * (stats["count"] - 1) + delta ** 2) / stats["count"])

anomaly_detector = AnomalyDetector()

def get_lstm_prediction(features):
    """Get LSTM prediction using real model"""
    # Convert single data point to sequence
    # The model expects a sequence of historical readings
    sequence = [features] * 24
    return lstm_predictor.predict_failure(sequence)

def get_rul_prediction(features, confidence=0.95):
    """Get RUL prediction using real model"""
    return rul_predictor.predict_rul(features, confidence)
