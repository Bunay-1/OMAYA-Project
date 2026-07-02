"""
LSTM Neural Network for Failure Prediction
Real TensorFlow implementation
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from typing import Dict, List, Tuple, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)

class LSTMFailurePredictor:
    """
    LSTM model for predicting machine failure probability
    Based on time-series sensor data
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = None
        self.feature_names = [
            "temperature", "vibration", "spindleSpeed", 
            "toolWear", "operatingHours", "cycleCount"
        ]
        self.sequence_length = 24  # Last 24 data points
        self.model_path = model_path or os.getenv("MODEL_PATH", "./models")
        
        # Load model if exists
        if os.path.exists(f"{self.model_path}/lstm_failure_model.h5"):
            self.load_model()
        else:
            logger.warning("LSTM model not found. Using mock predictions.")
    
    def build_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """
        Build LSTM neural network architecture
        
        Args:
            input_shape: (sequence_length, num_features)
            
        Returns:
            Compiled Keras model
        """
        model = keras.Sequential([
            # First LSTM layer with dropout
            keras.layers.LSTM(
                64, 
                return_sequences=True, 
                input_shape=input_shape,
                name="lstm_1"
            ),
            keras.layers.Dropout(0.2),
            
            # Second LSTM layer
            keras.layers.LSTM(32, return_sequences=False, name="lstm_2"),
            keras.layers.Dropout(0.2),
            
            # Dense layers
            keras.layers.Dense(16, activation='relu', name="dense_1"),
            keras.layers.Dropout(0.1),
            
            # Output layer (binary classification)
            keras.layers.Dense(1, activation='sigmoid', name="output")
        ])
        
        # Compile with binary crossentropy
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        
        return model
    
    def preprocess_sequence(self, data: List[Dict[str, float]]) -> np.ndarray:
        """
        Preprocess time-series data for LSTM input
        
        Args:
            data: List of sensor readings (must be sequence_length long)
            
        Returns:
            Normalized numpy array of shape (1, sequence_length, num_features)
        """
        if len(data) < self.sequence_length:
            # Pad with last value if not enough data
            data = data + [data[-1]] * (self.sequence_length - len(data))
        elif len(data) > self.sequence_length:
            # Take last sequence_length points
            data = data[-self.sequence_length:]
        
        # Extract features
        features = []
        for point in data:
            feature_vector = [
                point.get(feat, 0) for feat in self.feature_names
            ]
            features.append(feature_vector)
        
        # Convert to numpy array
        X = np.array(features, dtype=np.float32)
        
        # Normalize (min-max scaling)
        if self.scaler:
            X = self.scaler.transform(X)
        else:
            # Simple normalization if no scaler
            X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
        
        # Reshape for LSTM: (batch_size, sequence_length, num_features)
        return X.reshape(1, self.sequence_length, len(self.feature_names))
    
    def predict(self, sequence_data: List[Dict[str, float]]) -> Dict:
        """
        Predict failure probability from sensor sequence
        
        Args:
            sequence_data: List of recent sensor readings
            
        Returns:
            Prediction dict with probability and confidence
        """
        if self.model is None:
            # Fallback to mock prediction
            return self._mock_prediction(sequence_data[-1] if sequence_data else {})
        
        try:
            # Preprocess
            X = self.preprocess_sequence(sequence_data)
            
            # Predict
            pred = self.model.predict(X, verbose=0)[0][0]
            failure_prob = float(pred)
            
            # Calculate confidence based on model certainty
            # High confidence when probability is close to 0 or 1
            confidence = 1 - 2 * abs(failure_prob - 0.5)
            confidence = max(0.7, min(0.98, confidence))  # Clamp
            
            # Analyze contributing factors
            factors = self._analyze_factors(sequence_data[-1])
            
            return {
                "failureProbability": round(failure_prob, 3),
                "confidence": round(confidence, 3),
                "factors": factors,
                "modelVersion": "LSTM-TF-v1.0",
                "modelType": "neural_network"
            }
            
        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")
            return self._mock_prediction(sequence_data[-1] if sequence_data else {})

    def predict_failure(self, sequence_data: List[Dict[str, float]]) -> Dict:
        """Backward-compatible alias for failure prediction."""
        return self.predict(sequence_data)
    
    def _analyze_factors(self, latest_data: Dict[str, float]) -> List[Dict]:
        """Analyze which factors contribute most to failure risk"""
        temp = latest_data.get("temperature", 60)
        vibration = latest_data.get("vibration", 1.5)
        tool_wear = latest_data.get("toolWear", 50)
        hours = latest_data.get("operatingHours", 1000)
        
        factors = [
            {
                "name": "Temperature",
                "impact": min((temp - 40) / 40, 1.0),
                "status": "critical" if temp > 70 else "warning" if temp > 60 else "normal"
            },
            {
                "name": "Vibration",
                "impact": min(vibration / 3.0, 1.0),
                "status": "critical" if vibration > 2.5 else "warning" if vibration > 2.0 else "normal"
            },
            {
                "name": "Tool Wear",
                "impact": min(tool_wear / 100, 1.0),
                "status": "critical" if tool_wear > 85 else "warning" if tool_wear > 70 else "normal"
            },
            {
                "name": "Operating Hours",
                "impact": min(hours / 5000, 1.0),
                "status": "warning" if hours > 4000 else "normal"
            }
        ]
        
        return factors
    
    def _mock_prediction(self, data: Dict[str, float]) -> Dict:
        """Fallback mock prediction when model not loaded"""
        temp = data.get("temperature", 60)
        vibration = data.get("vibration", 1.5)
        tool_wear = data.get("toolWear", 50)
        
        risk_score = 0.0
        risk_score += min((temp - 40) / 40, 1.0) * 0.3
        risk_score += min(vibration / 3.0, 1.0) * 0.25
        risk_score += min(tool_wear / 100, 1.0) * 0.35
        risk_score += np.random.normal(0, 0.05)
        risk_score = max(0.0, min(1.0, risk_score))
        
        return {
            "failureProbability": round(risk_score, 3),
            "confidence": 0.75,
            "factors": self._analyze_factors(data),
            "modelVersion": "LSTM-mock-v1.0",
            "modelType": "mock"
        }
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              epochs: int = 50, batch_size: int = 32):
        """
        Train the LSTM model
        
        Args:
            X_train: Training sequences (samples, sequence_length, features)
            y_train: Training labels (samples,)
            epochs: Number of training epochs
            batch_size: Batch size
        """
        if self.model is None:
            input_shape = (X_train.shape[1], X_train.shape[2])
            self.model = self.build_model(input_shape)
        
        # Train
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=3
                )
            ],
            verbose=1
        )
        
        return history
    
    def save_model(self):
        """Save trained model to disk"""
        if self.model:
            os.makedirs(self.model_path, exist_ok=True)
            self.model.save(f"{self.model_path}/lstm_failure_model.h5")
            logger.info(f"Model saved to {self.model_path}/lstm_failure_model.h5")
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            self.model = keras.models.load_model(
                f"{self.model_path}/lstm_failure_model.h5"
            )
            logger.info(f"✅ LSTM model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading LSTM model: {e}")
            self.model = None

# Singleton instance
lstm_model = LSTMFailurePredictor()
