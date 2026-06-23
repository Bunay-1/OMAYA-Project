"""
Edge Computing Module
ONNX model conversion for edge deployment
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EdgeModelConverter:
    """
    Convert TensorFlow/Scikit-learn models to ONNX format
    for edge device deployment
    """
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = model_path
        self.onnx_available = self._check_onnx()
    
    def _check_onnx(self) -> bool:
        """Check if ONNX conversion libraries are available"""
        try:
            import tf2onnx
            import skl2onnx
            return True
        except ImportError:
            logger.warning("ONNX conversion libraries not available")
            return False
    
    def convert_lstm_to_onnx(self, model_name: str = "lstm_failure_model"):
        """
        Convert LSTM model to ONNX format
        
        Args:
            model_name: Name of the model file
        """
        if not self.onnx_available:
            logger.error("ONNX conversion not available. Install tf2onnx.")
            return False
        
        try:
            import tensorflow as tf
            import tf2onnx
            
            # Load TensorFlow model
            model_path = f"{self.model_path}/{model_name}.h5"
            if not os.path.exists(model_path):
                logger.error(f"Model not found: {model_path}")
                return False
            
            model = tf.keras.models.load_model(model_path)
            
            # Convert to ONNX
            onnx_model, _ = tf2onnx.convert.from_keras(model)
            
            # Save ONNX model
            onnx_path = f"{self.model_path}/{model_name}.onnx"
            with open(onnx_path, "wb") as f:
                f.write(onnx_model.SerializeToString())
            
            logger.info(f"✅ LSTM model converted to ONNX: {onnx_path}")
            return True
            
        except Exception as e:
            logger.error(f"ONNX conversion failed: {e}")
            return False
    
    def convert_sklearn_to_onnx(self, model_name: str = "rul_rf_model"):
        """
        Convert scikit-learn model to ONNX
        
        Args:
            model_name: Name of the model file
        """
        if not self.onnx_available:
            logger.error("ONNX conversion not available. Install skl2onnx.")
            return False
        
        try:
            import joblib
            from skl2onnx import convert_sklearn
            from skl2onnx.common.data_types import FloatTensorType
            
            # Load model
            model_path = f"{self.model_path}/{model_name}.pkl"
            if not os.path.exists(model_path):
                logger.error(f"Model not found: {model_path}")
                return False
            
            model = joblib.load(model_path)
            
            # Define input type (6 features)
            initial_type = [('float_input', FloatTensorType([None, 6]))]
            
            # Convert to ONNX
            onnx_model = convert_sklearn(model, initial_types=initial_type)
            
            # Save ONNX model
            onnx_path = f"{self.model_path}/{model_name}.onnx"
            with open(onnx_path, "wb") as f:
                f.write(onnx_model.SerializeToString())
            
            logger.info(f"✅ Sklearn model converted to ONNX: {onnx_path}")
            return True
            
        except Exception as e:
            logger.error(f"ONNX conversion failed: {e}")
            return False
    
    def get_model_info(self) -> dict:
        """Get information about available models"""
        models = {
            "tensorflow": [],
            "sklearn": [],
            "onnx": []
        }
        
        if os.path.exists(self.model_path):
            for file in os.listdir(self.model_path):
                if file.endswith(".h5"):
                    models["tensorflow"].append(file)
                elif file.endswith(".pkl"):
                    models["sklearn"].append(file)
                elif file.endswith(".onnx"):
                    models["onnx"].append(file)
        
        return models

# Singleton instance
edge_converter = EdgeModelConverter()
