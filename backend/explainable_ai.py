"""
Explainable AI Module
SHAP and LIME integration for model interpretability
"""
import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ExplainableAI:
    """
    Provides explanations for AI model predictions
    using SHAP and LIME
    """
    
    def __init__(self):
        self.shap_available = self._check_shap()
        self.lime_available = self._check_lime()
        self.feature_names = [
            "temperature", "vibration", "spindleSpeed",
            "toolWear", "operatingHours", "cycleCount"
        ]
    
    def _check_shap(self) -> bool:
        """Check if SHAP is available"""
        try:
            import shap
            return True
        except ImportError:
            logger.warning("SHAP not available. Install with: pip install shap")
            return False
    
    def _check_lime(self) -> bool:
        """Check if LIME is available"""
        try:
            import lime
            import lime.lime_tabular
            return True
        except ImportError:
            logger.warning("LIME not available. Install with: pip install lime")
            return False
    
    def explain_prediction_shap(
        self, 
        model: Any, 
        input_data: Dict[str, float],
        background_data: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Explain prediction using SHAP values
        
        Args:
            model: Trained model (sklearn or tensorflow)
            input_data: Input features
            background_data: Background dataset for SHAP
            
        Returns:
            Dict with SHAP explanation
        """
        if not self.shap_available:
            return self._mock_shap_explanation(input_data)
        
        try:
            import shap
            
            # Prepare input
            X = np.array([[input_data.get(f, 0) for f in self.feature_names]])
            
            # Generate background if not provided
            if background_data is None:
                background_data = np.random.randn(100, len(self.feature_names))
            
            # Create explainer based on model type
            if hasattr(model, 'predict_proba'):
                # Sklearn model
                explainer = shap.KernelExplainer(model.predict_proba, background_data)
            else:
                # General model
                explainer = shap.KernelExplainer(model.predict, background_data)
            
            # Calculate SHAP values
            shap_values = explainer.shap_values(X)
            
            # Format results
            if isinstance(shap_values, list):
                values = shap_values[1][0]  # For binary classification
            else:
                values = shap_values[0]
            
            contributions = {}
            for i, feat in enumerate(self.feature_names):
                contributions[feat] = {
                    "value": float(input_data.get(feat, 0)),
                    "shap_value": float(values[i]),
                    "impact": "positive" if values[i] > 0 else "negative",
                    "importance": abs(float(values[i]))
                }
            
            # Sort by importance
            sorted_features = sorted(
                contributions.items(), 
                key=lambda x: x[1]["importance"], 
                reverse=True
            )
            
            return {
                "method": "SHAP",
                "base_value": float(explainer.expected_value[1]) if isinstance(explainer.expected_value, list) else float(explainer.expected_value),
                "contributions": dict(sorted_features),
                "top_factors": [f[0] for f in sorted_features[:3]],
                "explanation": self._generate_explanation(sorted_features[:3])
            }
            
        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            return self._mock_shap_explanation(input_data)
    
    def explain_prediction_lime(
        self,
        model: Any,
        input_data: Dict[str, float],
        training_data: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Explain prediction using LIME
        
        Args:
            model: Trained model
            input_data: Input features
            training_data: Training dataset for LIME
            
        Returns:
            Dict with LIME explanation
        """
        if not self.lime_available:
            return self._mock_lime_explanation(input_data)
        
        try:
            from lime import lime_tabular
            
            # Prepare input
            X = np.array([input_data.get(f, 0) for f in self.feature_names])
            
            # Generate training data if not provided
            if training_data is None:
                training_data = np.random.randn(1000, len(self.feature_names))
            
            # Create LIME explainer
            explainer = lime_tabular.LimeTabularExplainer(
                training_data,
                feature_names=self.feature_names,
                class_names=['Normal', 'Failure'],
                mode='classification'
            )
            
            # Get prediction function
            if hasattr(model, 'predict_proba'):
                predict_fn = model.predict_proba
            else:
                predict_fn = lambda x: np.column_stack([1-model.predict(x), model.predict(x)])
            
            # Generate explanation
            exp = explainer.explain_instance(
                X,
                predict_fn,
                num_features=len(self.feature_names)
            )
            
            # Format results
            contributions = {}
            for feat, weight in exp.as_list():
                # Extract feature name from condition
                feat_name = feat.split()[0] if ' ' in feat else feat
                for f in self.feature_names:
                    if f in feat:
                        contributions[f] = {
                            "condition": feat,
                            "weight": float(weight),
                            "impact": "positive" if weight > 0 else "negative",
                            "importance": abs(float(weight))
                        }
                        break
            
            # Sort by importance
            sorted_features = sorted(
                contributions.items(),
                key=lambda x: x[1]["importance"],
                reverse=True
            )
            
            return {
                "method": "LIME",
                "prediction_probability": float(exp.predict_proba[1]),
                "contributions": dict(sorted_features),
                "top_factors": [f[0] for f in sorted_features[:3]],
                "explanation": self._generate_explanation(sorted_features[:3])
            }
            
        except Exception as e:
            logger.error(f"LIME explanation failed: {e}")
            return self._mock_lime_explanation(input_data)
    
    def _mock_shap_explanation(self, input_data: Dict[str, float]) -> Dict:
        """Generate mock SHAP explanation"""
        temp = input_data.get("temperature", 60)
        vibration = input_data.get("vibration", 1.5)
        tool_wear = input_data.get("toolWear", 50)
        
        contributions = {
            "toolWear": {
                "value": tool_wear,
                "shap_value": (tool_wear - 50) / 100 * 0.35,
                "impact": "positive" if tool_wear > 50 else "negative",
                "importance": abs((tool_wear - 50) / 100 * 0.35)
            },
            "temperature": {
                "value": temp,
                "shap_value": (temp - 60) / 40 * 0.3,
                "impact": "positive" if temp > 60 else "negative",
                "importance": abs((temp - 60) / 40 * 0.3)
            },
            "vibration": {
                "value": vibration,
                "shap_value": (vibration - 1.5) / 1.5 * 0.25,
                "impact": "positive" if vibration > 1.5 else "negative",
                "importance": abs((vibration - 1.5) / 1.5 * 0.25)
            },
            "operatingHours": {
                "value": input_data.get("operatingHours", 2000),
                "shap_value": 0.05,
                "impact": "positive",
                "importance": 0.05
            },
            "spindleSpeed": {
                "value": input_data.get("spindleSpeed", 10000),
                "shap_value": 0.03,
                "impact": "positive",
                "importance": 0.03
            },
            "cycleCount": {
                "value": input_data.get("cycleCount", 5000),
                "shap_value": 0.02,
                "impact": "positive",
                "importance": 0.02
            }
        }
        
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: x[1]["importance"],
            reverse=True
        )
        
        return {
            "method": "SHAP (mock)",
            "base_value": 0.15,
            "contributions": dict(sorted_features),
            "top_factors": [f[0] for f in sorted_features[:3]],
            "explanation": self._generate_explanation(sorted_features[:3])
        }
    
    def _mock_lime_explanation(self, input_data: Dict[str, float]) -> Dict:
        """Generate mock LIME explanation"""
        temp = input_data.get("temperature", 60)
        vibration = input_data.get("vibration", 1.5)
        tool_wear = input_data.get("toolWear", 50)
        
        contributions = {
            "toolWear": {
                "condition": f"toolWear > {tool_wear - 10:.0f}",
                "weight": 0.35 * (tool_wear / 100),
                "impact": "positive" if tool_wear > 50 else "negative",
                "importance": 0.35 * (tool_wear / 100)
            },
            "temperature": {
                "condition": f"temperature > {temp - 5:.0f}",
                "weight": 0.30 * ((temp - 40) / 40),
                "impact": "positive" if temp > 60 else "negative",
                "importance": 0.30 * ((temp - 40) / 40)
            },
            "vibration": {
                "condition": f"vibration > {vibration - 0.3:.1f}",
                "weight": 0.25 * (vibration / 3),
                "impact": "positive" if vibration > 1.5 else "negative",
                "importance": 0.25 * (vibration / 3)
            }
        }
        
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: x[1]["importance"],
            reverse=True
        )
        
        risk = (tool_wear / 100 * 0.35) + ((temp - 40) / 40 * 0.3) + (vibration / 3 * 0.25)
        
        return {
            "method": "LIME (mock)",
            "prediction_probability": min(0.95, risk),
            "contributions": dict(sorted_features),
            "top_factors": [f[0] for f in sorted_features[:3]],
            "explanation": self._generate_explanation(sorted_features[:3])
        }
    
    def _generate_explanation(self, top_features: List[tuple]) -> str:
        """Generate human-readable explanation"""
        if not top_features:
            return "No significant factors identified."
        
        explanations = []
        for feat_name, data in top_features:
            impact = data.get("impact", "positive")
            importance = data.get("importance", 0)
            
            if importance > 0.2:
                strength = "strongly"
            elif importance > 0.1:
                strength = "moderately"
            else:
                strength = "slightly"
            
            direction = "increases" if impact == "positive" else "decreases"
            
            # Format feature name for display
            display_name = {
                "temperature": "Temperature",
                "vibration": "Vibration level",
                "toolWear": "Tool wear",
                "spindleSpeed": "Spindle speed",
                "operatingHours": "Operating hours",
                "cycleCount": "Cycle count"
            }.get(feat_name, feat_name)
            
            explanations.append(f"{display_name} {strength} {direction} failure risk")
        
        return ". ".join(explanations) + "."
    
    def get_feature_importance(self, model: Any) -> Dict[str, float]:
        """
        Get global feature importance from model
        
        Args:
            model: Trained model
            
        Returns:
            Dict of feature importances
        """
        # For sklearn models with feature_importances_
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            return {
                feat: float(imp) 
                for feat, imp in zip(self.feature_names, importances)
            }
        
        # Mock importance for other models
        return {
            "toolWear": 0.35,
            "temperature": 0.28,
            "vibration": 0.22,
            "operatingHours": 0.08,
            "spindleSpeed": 0.04,
            "cycleCount": 0.03
        }

# Singleton instance
explainable_ai = ExplainableAI()
