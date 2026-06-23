"""
RUL (Remaining Useful Life) Prediction Model
Using survival analysis and regression
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class RULPredictor:
    """
    Remaining Useful Life predictor using ensemble methods
    Combines Random Forest and Gradient Boosting
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.rf_model = None
        self.gb_model = None
        self.scaler = None
        self.feature_names = [
            "temperature", "vibration", "spindleSpeed",
            "toolWear", "operatingHours", "cycleCount"
        ]
        self.model_path = model_path or os.getenv("MODEL_PATH", "./models")
        
        # Try to load models
        self._load_models()
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            rf_path = f"{self.model_path}/rul_rf_model.pkl"
            gb_path = f"{self.model_path}/rul_gb_model.pkl"
            scaler_path = f"{self.model_path}/rul_scaler.pkl"
            
            if os.path.exists(rf_path) and os.path.exists(gb_path):
                self.rf_model = joblib.load(rf_path)
                self.gb_model = joblib.load(gb_path)
                
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                
                logger.info("✅ RUL models loaded successfully")
            else:
                logger.warning("RUL models not found. Using mock predictions.")
        except Exception as e:
            logger.error(f"Error loading RUL models: {e}")
    
    def build_models(self):
        """Initialize ensemble models"""
        # Random Forest for RUL prediction
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Gradient Boosting for RUL prediction
        self.gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=5,
            random_state=42
        )
        
        # Standard scaler
        self.scaler = StandardScaler()
    
    def preprocess_features(self, data: Dict[str, float]) -> np.ndarray:
        """
        Extract and preprocess features
        
        Args:
            data: Sensor readings
            
        Returns:
            Feature vector as numpy array
        """
        features = [data.get(feat, 0) for feat in self.feature_names]
        X = np.array(features, dtype=np.float32).reshape(1, -1)
        
        if self.scaler:
            X = self.scaler.transform(X)
        
        return X
    
    def predict(self, data: Dict[str, float], confidence_level: float = 0.95) -> Dict:
        """
        Predict Remaining Useful Life with confidence intervals
        
        Args:
            data: Current sensor readings
            confidence_level: Confidence level for intervals (0.95 = 95%)
            
        Returns:
            Dict with RUL estimate and confidence intervals
        """
        if self.rf_model is None or self.gb_model is None:
            return self._mock_prediction(data, confidence_level)
        
        try:
            # Preprocess
            X = self.preprocess_features(data)
            
            # Ensemble prediction (average of RF and GB)
            rf_pred = self.rf_model.predict(X)[0]
            gb_pred = self.gb_model.predict(X)[0]
            mean_rul = (rf_pred + gb_pred) / 2
            
            # Estimate uncertainty using tree predictions
            if hasattr(self.rf_model, 'estimators_'):
                tree_preds = [tree.predict(X)[0] for tree in self.rf_model.estimators_]
                std_dev = np.std(tree_preds)
            else:
                std_dev = mean_rul * 0.15
            
            # Confidence intervals
            z_score = 1.96 if confidence_level == 0.95 else 2.576
            lower_bound = max(0, mean_rul - z_score * std_dev)
            upper_bound = mean_rul + z_score * std_dev
            
            # Convert to days
            days_lower = lower_bound / 24
            days_mean = mean_rul / 24
            days_upper = upper_bound / 24
            
            return {
                "rul_hours": round(mean_rul, 1),
                "rul_days": round(days_mean, 1),
                "confidence_interval": {
                    "lower_hours": round(lower_bound, 1),
                    "upper_hours": round(upper_bound, 1),
                    "lower_days": round(days_lower, 1),
                    "upper_days": round(days_upper, 1),
                    "confidence": confidence_level
                },
                "uncertainty": round(std_dev / mean_rul, 3),
                "recommended_action": self._get_recommendation(mean_rul),
                "modelVersion": "Ensemble-RF-GB-v1.0",
                "modelType": "ensemble_regression"
            }
            
        except Exception as e:
            logger.error(f"RUL prediction error: {e}")
            return self._mock_prediction(data, confidence_level)
    
    def _mock_prediction(self, data: Dict[str, float], confidence_level: float) -> Dict:
        """Fallback mock prediction"""
        temp = data.get("temperature", 60)
        vibration = data.get("vibration", 1.5)
        tool_wear = data.get("toolWear", 50)
        
        base_rul = 1000
        temp_factor = max(0.3, 1 - (temp - 40) / 80)
        vibration_factor = max(0.3, 1 - vibration / 4)
        wear_factor = max(0.2, 1 - tool_wear / 150)
        
        mean_rul = base_rul * temp_factor * vibration_factor * wear_factor
        mean_rul = max(10, mean_rul)
        
        std_dev = mean_rul * (0.15 + (1 - wear_factor) * 0.1)
        z_score = 1.96 if confidence_level == 0.95 else 2.576
        
        lower_bound = max(0, mean_rul - z_score * std_dev)
        upper_bound = mean_rul + z_score * std_dev
        
        return {
            "rul_hours": round(mean_rul, 1),
            "rul_days": round(mean_rul / 24, 1),
            "confidence_interval": {
                "lower_hours": round(lower_bound, 1),
                "upper_hours": round(upper_bound, 1),
                "lower_days": round(lower_bound / 24, 1),
                "upper_days": round(upper_bound / 24, 1),
                "confidence": confidence_level
            },
            "uncertainty": round(std_dev / mean_rul, 3),
            "recommended_action": self._get_recommendation(mean_rul),
            "modelVersion": "RUL-mock-v1.0",
            "modelType": "mock"
        }
    
    def _get_recommendation(self, rul_hours: float) -> str:
        """Get maintenance recommendation based on RUL"""
        if rul_hours < 24:
            return "URGENT: Schedule immediate maintenance"
        elif rul_hours < 72:
            return "CRITICAL: Schedule maintenance within 3 days"
        elif rul_hours < 168:
            return "WARNING: Schedule maintenance within 1 week"
        elif rul_hours < 336:
            return "ADVISORY: Plan maintenance within 2 weeks"
        else:
            return "NORMAL: Continue monitoring"
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Train ensemble models
        
        Args:
            X_train: Training features
            y_train: Training RUL values (in hours)
        """
        if self.rf_model is None or self.gb_model is None:
            self.build_models()
        
        # Fit scaler
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Train models
        logger.info("Training Random Forest...")
        self.rf_model.fit(X_scaled, y_train)
        
        logger.info("Training Gradient Boosting...")
        self.gb_model.fit(X_scaled, y_train)
        
        logger.info("✅ RUL models trained successfully")
    
    def save_models(self):
        """Save trained models to disk"""
        os.makedirs(self.model_path, exist_ok=True)
        
        if self.rf_model:
            joblib.dump(self.rf_model, f"{self.model_path}/rul_rf_model.pkl")
        if self.gb_model:
            joblib.dump(self.gb_model, f"{self.model_path}/rul_gb_model.pkl")
        if self.scaler:
            joblib.dump(self.scaler, f"{self.model_path}/rul_scaler.pkl")
        
        logger.info(f"Models saved to {self.model_path}")

# Singleton instance
rul_model = RULPredictor()
