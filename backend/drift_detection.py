"""
Model Drift Detection
Monitor model performance degradation over time
"""
import numpy as np
from collections import deque
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DriftDetector:
    """
    Detect model drift by monitoring prediction accuracy
    and feature distributions
    """
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.actuals = deque(maxlen=window_size)
        self.feature_distributions = {}
        self.baseline_accuracy = None
        self.drift_threshold = 0.1  # 10% accuracy drop
        
    def add_prediction(self, prediction: float, actual: float, features: Dict):
        """
        Add a prediction-actual pair with features
        
        Args:
            prediction: Model prediction
            actual: Ground truth
            features: Input features used
        """
        self.predictions.append(prediction)
        self.actuals.append(actual)
        
        # Update feature distributions
        for key, value in features.items():
            if key not in self.feature_distributions:
                self.feature_distributions[key] = deque(maxlen=self.window_size)
            self.feature_distributions[key].append(value)
    
    def calculate_accuracy(self) -> float:
        """Calculate current model accuracy"""
        if len(self.predictions) < 50:
            return 1.0  # Not enough data
        
        # Binary classification accuracy
        preds = np.array(self.predictions)
        actuals = np.array(self.actuals)
        
        # Convert probabilities to binary (threshold 0.5)
        binary_preds = (preds > 0.5).astype(int)
        binary_actuals = (actuals > 0.5).astype(int)
        
        accuracy = (binary_preds == binary_actuals).mean()
        
        if self.baseline_accuracy is None:
            self.baseline_accuracy = accuracy
        
        return accuracy
    
    def detect_drift(self) -> Dict:
        """
        Detect if model has drifted
        
        Returns:
            Dict with drift detection results
        """
        if len(self.predictions) < 100:
            return {
                "hasDrift": False,
                "reason": "Insufficient data for drift detection",
                "samplesCollected": len(self.predictions)
            }
        
        current_accuracy = self.calculate_accuracy()
        
        # Check accuracy drift
        accuracy_drift = False
        if self.baseline_accuracy:
            accuracy_drop = self.baseline_accuracy - current_accuracy
            accuracy_drift = accuracy_drop > self.drift_threshold
        
        # Check feature distribution drift (PSI - Population Stability Index)
        feature_drift_scores = {}
        for feature, values in self.feature_distributions.items():
            if len(values) >= 100:
                psi = self._calculate_psi(list(values))
                feature_drift_scores[feature] = round(psi, 3)
        
        max_psi = max(feature_drift_scores.values()) if feature_drift_scores else 0
        feature_drift = max_psi > 0.2  # PSI > 0.2 indicates drift
        
        has_drift = accuracy_drift or feature_drift
        
        return {
            "hasDrift": has_drift,
            "accuracyDrift": accuracy_drift,
            "featureDrift": feature_drift,
            "currentAccuracy": round(current_accuracy, 3),
            "baselineAccuracy": round(self.baseline_accuracy, 3) if self.baseline_accuracy else None,
            "accuracyDrop": round(self.baseline_accuracy - current_accuracy, 3) if self.baseline_accuracy else 0,
            "featureDriftScores": feature_drift_scores,
            "maxPSI": round(max_psi, 3),
            "samplesAnalyzed": len(self.predictions),
            "recommendation": self._get_recommendation(has_drift, accuracy_drift, feature_drift)
        }
    
    def _calculate_psi(self, values: List[float]) -> float:
        """
        Calculate Population Stability Index
        Compares current distribution to baseline (first half)
        """
        if len(values) < 100:
            return 0.0
        
        # Split into baseline and current
        split_point = len(values) // 2
        baseline = values[:split_point]
        current = values[split_point:]
        
        # Create 10 bins
        bins = np.percentile(baseline, np.linspace(0, 100, 11))
        
        # Calculate distribution in each bin
        baseline_dist, _ = np.histogram(baseline, bins=bins)
        current_dist, _ = np.histogram(current, bins=bins)
        
        # Avoid division by zero
        baseline_dist = (baseline_dist + 1) / (len(baseline) + 10)
        current_dist = (current_dist + 1) / (len(current) + 10)
        
        # Calculate PSI
        psi = np.sum((current_dist - baseline_dist) * np.log(current_dist / baseline_dist))
        
        return abs(psi)
    
    def _get_recommendation(self, has_drift: bool, accuracy_drift: bool, feature_drift: bool) -> str:
        """Get recommendation based on drift detection"""
        if not has_drift:
            return "No drift detected. Model performing normally."
        
        if accuracy_drift and feature_drift:
            return "CRITICAL: Both accuracy and feature drift detected. Retrain model immediately."
        elif accuracy_drift:
            return "WARNING: Accuracy drift detected. Consider retraining model."
        elif feature_drift:
            return "ADVISORY: Feature distribution drift detected. Monitor closely."
        else:
            return "Model monitoring active."
    
    def reset(self):
        """Reset drift detector"""
        self.predictions.clear()
        self.actuals.clear()
        self.feature_distributions.clear()
        self.baseline_accuracy = None

# Singleton instance
drift_detector = DriftDetector()
