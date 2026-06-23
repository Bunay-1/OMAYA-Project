"""
Model Training Script
Train LSTM and RUL models on historical OMAYA data
"""
import numpy as np
import pandas as pd
from lstm_model import lstm_model
from rul_model import rul_model
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthetic_training_data(num_samples: int = 10000):
    """
    Generate synthetic training data for demonstration
    In production, replace with real historical data
    """
    logger.info(f"Generating {num_samples} synthetic training samples...")
    
    # Generate features
    temperatures = np.random.normal(60, 10, num_samples)
    vibrations = np.random.normal(1.5, 0.5, num_samples)
    spindle_speeds = np.random.normal(10000, 1000, num_samples)
    tool_wear = np.random.uniform(0, 100, num_samples)
    operating_hours = np.random.uniform(0, 5000, num_samples)
    cycle_counts = np.random.uniform(0, 10000, num_samples)
    
    # Generate labels (failure probability and RUL)
    # Simple rule-based labels for demonstration
    failure_prob = (
        0.3 * (temperatures > 70) +
        0.25 * (vibrations > 2.0) +
        0.35 * (tool_wear > 70) +
        0.1 * (operating_hours > 4000)
    )
    failure_prob = np.clip(failure_prob + np.random.normal(0, 0.1, num_samples), 0, 1)
    
    # RUL calculation (inverse relationship with degradation)
    rul = 1000 * (1 - failure_prob) * np.random.uniform(0.8, 1.2, num_samples)
    rul = np.maximum(rul, 10)  # Minimum 10 hours
    
    # Binary labels for LSTM (failure if prob > 0.7)
    binary_labels = (failure_prob > 0.7).astype(int)
    
    return {
        "features": np.column_stack([
            temperatures, vibrations, spindle_speeds,
            tool_wear, operating_hours, cycle_counts
        ]),
        "failure_labels": binary_labels,
        "rul_labels": rul
    }

def create_lstm_sequences(features: np.ndarray, labels: np.ndarray, 
                          sequence_length: int = 24):
    """
    Create time-series sequences for LSTM training
    """
    X, y = [], []
    
    for i in range(len(features) - sequence_length):
        X.append(features[i:i + sequence_length])
        y.append(labels[i + sequence_length])
    
    return np.array(X), np.array(y)

def train_lstm():
    """Train LSTM failure prediction model"""
    logger.info("=" * 50)
    logger.info("Training LSTM Failure Prediction Model")
    logger.info("=" * 50)
    
    # Generate data
    data = generate_synthetic_training_data(num_samples=10000)
    
    # Create sequences
    X_seq, y_seq = create_lstm_sequences(
        data["features"], 
        data["failure_labels"],
        sequence_length=24
    )
    
    logger.info(f"Training data shape: {X_seq.shape}")
    logger.info(f"Labels shape: {y_seq.shape}")
    
    # Train
    history = lstm_model.train(
        X_seq, y_seq,
        epochs=30,
        batch_size=32
    )
    
    # Save
    lstm_model.save_model()
    
    logger.info("✅ LSTM model training complete")
    
    return history

def train_rul():
    """Train RUL prediction ensemble"""
    logger.info("=" * 50)
    logger.info("Training RUL Prediction Ensemble")
    logger.info("=" * 50)
    
    # Generate data
    data = generate_synthetic_training_data(num_samples=10000)
    
    X = data["features"]
    y = data["rul_labels"]
    
    logger.info(f"Training data shape: {X.shape}")
    logger.info(f"RUL labels shape: {y.shape}")
    
    # Train
    rul_model.train(X, y)
    
    # Save
    rul_model.save_models()
    
    logger.info("✅ RUL model training complete")

if __name__ == "__main__":
    logger.info("🚀 Starting model training pipeline...")
    
    # Train LSTM
    try:
        train_lstm()
    except Exception as e:
        logger.error(f"LSTM training failed: {e}")
    
    # Train RUL
    try:
        train_rul()
    except Exception as e:
        logger.error(f"RUL training failed: {e}")
    
    logger.info("🎉 Training pipeline complete!")
