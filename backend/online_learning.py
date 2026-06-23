"""
Online Learning Module
Adaptive anomaly detection with streaming updates
"""
import numpy as np
from collections import deque
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class OnlineAnomalyDetector:
    """
    Online learning anomaly detector
    Updates model incrementally with new data
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.feature_windows = {
            "temperature": deque(maxlen=window_size),
            "vibration": deque(maxlen=window_size),
            "spindleSpeed": deque(maxlen=window_size),
        }
        self.means = {}
        self.stds = {}
        self.trained = False
        
    def update(self, data: Dict[str, float]):
        """
        Update model with new data point
        
        Args:
            data: Sensor readings
        """
        for feature in ["temperature", "vibration", "spindleSpeed"]:
            value = data.get(feature, 0)
            self.feature_windows[feature].append(value)
        
        # Recalculate statistics
        if len(self.feature_windows["temperature"]) >= 20:
            for feature, window in self.feature_windows.items():
                self.means[feature] = np.mean(window)
                self.stds[feature] = np.std(window)
            self.trained = True
    
    def predict(self, data: Dict[str, float]) -> Dict:
        """
        Predict if data point is anomalous
        
        Args:
            data: Sensor readings
            
        Returns:
            Prediction with anomaly score
        """
        if not self.trained:
            # Not enough data yet
            return {
                "isAnomalous": False,
                "anomalyScore": 0.0,
                "reason": "Model training in progress"
            }
        
        # Calculate z-scores
        z_scores = {}
        for feature in ["temperature", "vibration", "spindleSpeed"]:
            value = data.get(feature, 0)
            mean = self.means.get(feature, value)
            std = self.stds.get(feature, 1.0)
            
            if std > 0:
                z_scores[feature] = abs((value - mean) / std)
            else:
                z_scores[feature] = 0
        
        # Anomaly if any z-score > 3 (3 sigma rule)
        max_z_score = max(z_scores.values())
        is_anomalous = max_z_score > 3.0
        
        # Update model with new data
        self.update(data)
        
        return {
            "isAnomalous": is_anomalous,
            "anomalyScore": round(min(max_z_score / 5.0, 1.0), 3),
            "zScores": {k: round(v, 2) for k, v in z_scores.items()},
            "threshold": 3.0,
            "samplesUsed": len(self.feature_windows["temperature"])
        }
    
    def get_statistics(self) -> Dict:
        """Get current model statistics"""
        return {
            "means": {k: round(v, 2) for k, v in self.means.items()},
            "stds": {k: round(v, 2) for k, v in self.stds.items()},
            "trained": self.trained,
            "windowSize": self.window_size
        }

# Singleton instance
online_detector = OnlineAnomalyDetector()
