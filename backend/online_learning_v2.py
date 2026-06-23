"""
Online Learning v2.0 for OMAYA Platform
Continuous model training and adaptation with drift detection
"""
from typing import Dict, Any, Optional, List, Tuple
import logging
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
import tensorflow as tf
from tensorflow import keras
import pickle
import os

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc: float
    timestamp: datetime


@dataclass
class DriftDetectionResult:
    """Drift detection result."""
    has_drift: bool
    drift_score: float
    drift_type: str  # 'covariate', 'concept', 'label'
    timestamp: datetime


class ConceptDriftDetector:
    """Detect concept drift in data distribution."""
    
    def __init__(self, threshold: float = 0.1, window_size: int = 1000):
        """
        Initialize drift detector.
        
        Args:
            threshold: Drift detection threshold
            window_size: Window size for comparison
        """
        self.threshold = threshold
        self.window_size = window_size
        self.reference_data: List[np.ndarray] = []
        self.current_data: List[np.ndarray] = []
    
    def add_reference_data(self, data: np.ndarray):
        """Add reference data for comparison."""
        self.reference_data.append(data)
        if len(self.reference_data) > self.window_size:
            self.reference_data.pop(0)
    
    def add_current_data(self, data: np.ndarray):
        """Add current data for drift detection."""
        self.current_data.append(data)
        if len(self.current_data) > self.window_size:
            self.current_data.pop(0)
    
    def detect_drift(self) -> DriftDetectionResult:
        """
        Detect concept drift.
        
        Returns:
            DriftDetectionResult
        """
        if not self.reference_data or not self.current_data:
            return DriftDetectionResult(
                has_drift=False,
                drift_score=0.0,
                drift_type='none',
                timestamp=datetime.now()
            )
        
        ref_array = np.vstack(self.reference_data)
        cur_array = np.vstack(self.current_data)
        
        # Calculate KL divergence
        drift_score = self._calculate_kl_divergence(ref_array, cur_array)
        
        has_drift = drift_score > self.threshold
        drift_type = 'concept' if has_drift else 'none'
        
        return DriftDetectionResult(
            has_drift=has_drift,
            drift_score=drift_score,
            drift_type=drift_type,
            timestamp=datetime.now()
        )
    
    def _calculate_kl_divergence(self, ref: np.ndarray, cur: np.ndarray) -> float:
        """Calculate KL divergence between distributions."""
        # Simplified KL divergence calculation
        ref_mean = np.mean(ref, axis=0)
        cur_mean = np.mean(cur, axis=0)
        
        ref_std = np.std(ref, axis=0) + 1e-10
        cur_std = np.std(cur, axis=0) + 1e-10
        
        kl = 0.5 * np.sum(
            np.log(cur_std / ref_std) +
            (ref_std ** 2 + (ref_mean - cur_mean) ** 2) / (2 * cur_std ** 2) -
            0.5
        )
        
        return float(kl)


class OnlineLearner:
    """Online learning with incremental model updates."""
    
    def __init__(self, model: keras.Model, learning_rate: float = 0.001):
        """
        Initialize online learner.
        
        Args:
            model: Base Keras model
            learning_rate: Learning rate for online updates
        """
        self.model = model
        self.learning_rate = learning_rate
        self.optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
        self.metrics_history: List[ModelMetrics] = []
        self.drift_detector = ConceptDriftDetector()
        self.update_count = 0
    
    def update_model(self, X: np.ndarray, y: np.ndarray, 
                    batch_size: int = 32, epochs: int = 1) -> ModelMetrics:
        """
        Update model with new data.
        
        Args:
            X: Feature data
            y: Target data
            batch_size: Batch size for training
            epochs: Number of training epochs
            
        Returns:
            ModelMetrics
        """
        # Detect drift before update
        self.drift_detector.add_current_data(X)
        drift_result = self.drift_detector.detect_drift()
        
        if drift_result.has_drift:
            logger.warning(f"Concept drift detected: {drift_result.drift_score:.4f}")
        
        # Train model on new data
        history = self.model.fit(
            X, y,
            batch_size=batch_size,
            epochs=epochs,
            verbose=0,
            shuffle=True
        )
        
        # Calculate metrics
        y_pred = self.model.predict(X, verbose=0)
        metrics = self._calculate_metrics(y, y_pred)
        
        self.metrics_history.append(metrics)
        self.update_count += 1
        
        logger.info(f"Model updated (update #{self.update_count}): accuracy={metrics.accuracy:.4f}")
        
        return metrics
    
    def _calculate_metrics(self, y_true: np.ndarray, 
                          y_pred: np.ndarray) -> ModelMetrics:
        """Calculate model metrics."""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        # Convert probabilities to binary predictions
        y_pred_binary = (y_pred > 0.5).astype(int)
        
        accuracy = accuracy_score(y_true, y_pred_binary)
        precision = precision_score(y_true, y_pred_binary, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred_binary, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred_binary, average='weighted', zero_division=0)
        
        try:
            auc = roc_auc_score(y_true, y_pred)
        except:
            auc = 0.0
        
        return ModelMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc=auc,
            timestamp=datetime.now()
        )
    
    def get_metrics_history(self) -> List[ModelMetrics]:
        """Get metrics history."""
        return self.metrics_history
    
    def save_model(self, path: str):
        """Save model to disk."""
        self.model.save(path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model from disk."""
        self.model = keras.models.load_model(path)
        logger.info(f"Model loaded from {path}")


class IncrementalLearner:
    """Incremental learning for large datasets."""
    
    def __init__(self, model: keras.Model, buffer_size: int = 10000):
        """
        Initialize incremental learner.
        
        Args:
            model: Base Keras model
            buffer_size: Size of replay buffer
        """
        self.model = model
        self.buffer_size = buffer_size
        self.X_buffer: List[np.ndarray] = []
        self.y_buffer: List[np.ndarray] = []
        self.update_count = 0
    
    def add_data(self, X: np.ndarray, y: np.ndarray):
        """Add data to replay buffer."""
        self.X_buffer.append(X)
        self.y_buffer.append(y)
        
        # Maintain buffer size
        total_samples = sum(len(x) for x in self.X_buffer)
        while total_samples > self.buffer_size:
            self.X_buffer.pop(0)
            self.y_buffer.pop(0)
            total_samples = sum(len(x) for x in self.X_buffer)
    
    def train_incremental(self, batch_size: int = 32, epochs: int = 1):
        """Train on buffered data incrementally."""
        if not self.X_buffer:
            logger.warning("No data in buffer for incremental training")
            return
        
        X_combined = np.vstack(self.X_buffer)
        y_combined = np.vstack(self.y_buffer)
        
        # Shuffle data
        indices = np.random.permutation(len(X_combined))
        X_combined = X_combined[indices]
        y_combined = y_combined[indices]
        
        # Train
        history = self.model.fit(
            X_combined, y_combined,
            batch_size=batch_size,
            epochs=epochs,
            verbose=0
        )
        
        self.update_count += 1
        logger.info(f"Incremental training completed (update #{self.update_count})")
        
        return history


class AdaptiveLearningRate:
    """Adaptive learning rate scheduler."""
    
    def __init__(self, initial_lr: float = 0.001, min_lr: float = 1e-6,
                 max_lr: float = 0.1, factor: float = 0.5):
        """
        Initialize adaptive learning rate.
        
        Args:
            initial_lr: Initial learning rate
            min_lr: Minimum learning rate
            max_lr: Maximum learning rate
            factor: Reduction factor
        """
        self.initial_lr = initial_lr
        self.min_lr = min_lr
        self.max_lr = max_lr
        self.factor = factor
        self.current_lr = initial_lr
        self.best_loss = float('inf')
        self.patience = 5
        self.wait = 0
    
    def update(self, loss: float) -> float:
        """
        Update learning rate based on loss.
        
        Args:
            loss: Current loss value
            
        Returns:
            New learning rate
        """
        if loss < self.best_loss:
            self.best_loss = loss
            self.wait = 0
        else:
            self.wait += 1
        
        if self.wait >= self.patience:
            self.current_lr = max(self.min_lr, self.current_lr * self.factor)
            self.wait = 0
            logger.info(f"Learning rate reduced to {self.current_lr:.6f}")
        
        return self.current_lr
    
    def reset(self):
        """Reset learning rate to initial value."""
        self.current_lr = self.initial_lr
        self.best_loss = float('inf')
        self.wait = 0


class ModelEnsemble:
    """Ensemble of models for robust predictions."""
    
    def __init__(self, models: List[keras.Model], weights: List[float] = None):
        """
        Initialize model ensemble.
        
        Args:
            models: List of Keras models
            weights: Optional weights for each model
        """
        self.models = models
        self.weights = weights or [1.0 / len(models)] * len(models)
        self.metrics_history: List[ModelMetrics] = []
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make ensemble prediction.
        
        Args:
            X: Input data
            
        Returns:
            Weighted average of predictions
        """
        predictions = []
        for model in self.models:
            pred = model.predict(X, verbose=0)
            predictions.append(pred)
        
        # Weighted average
        ensemble_pred = np.average(predictions, axis=0, weights=self.weights)
        return ensemble_pred
    
    def update_ensemble(self, X: np.ndarray, y: np.ndarray, 
                       batch_size: int = 32, epochs: int = 1):
        """Update all models in ensemble."""
        for i, model in enumerate(self.models):
            model.fit(X, y, batch_size=batch_size, epochs=epochs, verbose=0)
            logger.info(f"Model {i+1}/{len(self.models)} updated")
    
    def evaluate_ensemble(self, X: np.ndarray, y: np.ndarray) -> ModelMetrics:
        """Evaluate ensemble performance."""
        y_pred = self.predict(X)
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        y_pred_binary = (y_pred > 0.5).astype(int)
        
        accuracy = accuracy_score(y, y_pred_binary)
        precision = precision_score(y, y_pred_binary, average='weighted', zero_division=0)
        recall = recall_score(y, y_pred_binary, average='weighted', zero_division=0)
        f1 = f1_score(y, y_pred_binary, average='weighted', zero_division=0)
        
        try:
            auc = roc_auc_score(y, y_pred)
        except:
            auc = 0.0
        
        metrics = ModelMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc=auc,
            timestamp=datetime.now()
        )
        
        self.metrics_history.append(metrics)
        return metrics


class ActiveLearning:
    """Active learning for efficient data labeling."""
    
    def __init__(self, model: keras.Model, uncertainty_threshold: float = 0.5):
        """
        Initialize active learning.
        
        Args:
            model: Trained model
            uncertainty_threshold: Threshold for uncertain samples
        """
        self.model = model
        self.uncertainty_threshold = uncertainty_threshold
        self.unlabeled_data: List[np.ndarray] = []
    
    def add_unlabeled_data(self, X: np.ndarray):
        """Add unlabeled data."""
        self.unlabeled_data.append(X)
    
    def select_samples_for_labeling(self, n_samples: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Select most uncertain samples for labeling.
        
        Args:
            n_samples: Number of samples to select
            
        Returns:
            Tuple of (samples, uncertainties)
        """
        if not self.unlabeled_data:
            return np.array([]), np.array([])
        
        X_unlabeled = np.vstack(self.unlabeled_data)
        
        # Get predictions
        predictions = self.model.predict(X_unlabeled, verbose=0)
        
        # Calculate uncertainty (entropy)
        uncertainties = -predictions * np.log(predictions + 1e-10) - \
                       (1 - predictions) * np.log(1 - predictions + 1e-10)
        uncertainties = np.mean(uncertainties, axis=1)
        
        # Select top uncertain samples
        top_indices = np.argsort(uncertainties)[-n_samples:]
        selected_samples = X_unlabeled[top_indices]
        selected_uncertainties = uncertainties[top_indices]
        
        return selected_samples, selected_uncertainties
    
    def update_with_labeled_data(self, X: np.ndarray, y: np.ndarray, 
                                 batch_size: int = 32, epochs: int = 1):
        """Update model with newly labeled data."""
        self.model.fit(X, y, batch_size=batch_size, epochs=epochs, verbose=0)
        logger.info("Model updated with labeled data")


class ModelVersioning:
    """Model versioning and rollback capabilities."""
    
    def __init__(self, storage_path: str = "model_versions"):
        """
        Initialize model versioning.
        
        Args:
            storage_path: Path to store model versions
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.versions: Dict[str, Dict[str, Any]] = {}
    
    def save_version(self, model: keras.Model, version: str, 
                    metrics: ModelMetrics, metadata: Dict[str, Any] = None):
        """
        Save model version.
        
        Args:
            model: Keras model to save
            version: Version identifier
            metrics: Model metrics
            metadata: Additional metadata
        """
        version_path = os.path.join(self.storage_path, version)
        os.makedirs(version_path, exist_ok=True)
        
        # Save model
        model_path = os.path.join(version_path, "model.keras")
        model.save(model_path)
        
        # Save metadata
        version_info = {
            'version': version,
            'metrics': {
                'accuracy': metrics.accuracy,
                'precision': metrics.precision,
                'recall': metrics.recall,
                'f1_score': metrics.f1_score,
                'auc': metrics.auc,
                'timestamp': metrics.timestamp.isoformat()
            },
            'metadata': metadata or {},
            'path': version_path
        }
        
        self.versions[version] = version_info
        
        # Save version info
        info_path = os.path.join(version_path, "info.pkl")
        with open(info_path, 'wb') as f:
            pickle.dump(version_info, f)
        
        logger.info(f"Model version {version} saved")
    
    def load_version(self, version: str) -> keras.Model:
        """
        Load model version.
        
        Args:
            version: Version identifier
            
        Returns:
            Loaded Keras model
        """
        if version not in self.versions:
            raise ValueError(f"Version {version} not found")
        
        model_path = os.path.join(self.versions[version]['path'], "model.keras")
        model = keras.models.load_model(model_path)
        
        logger.info(f"Model version {version} loaded")
        return model
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all available versions."""
        return list(self.versions.values())
    
    def rollback(self, version: str) -> keras.Model:
        """
        Rollback to specific version.
        
        Args:
            version: Version to rollback to
            
        Returns:
            Loaded model
        """
        logger.warning(f"Rolling back to version {version}")
        return self.load_version(version)
