"""
ML Engine for brain stroke detection.
Integrates TensorFlow model with preprocessing and validation.
Uses ResNet50 Ensemble model for improved accuracy.
"""

import numpy as np
import logging
from typing import Dict, Optional

# Try to import TensorFlow - it may not be installed on Python 3.14 yet
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None

# Import our preprocessing module
from apps.ai.preprocessing import (
    preprocess_image,
    validate_mri,
    validate_image_format,
    CLASSES,
    CONFIDENCE_THRESHOLD,
)

try:
    from apps.ai.model_loader import get_model, model_ready
except ImportError:
    # If model_loader fails to import, create placeholder
    def get_model():
        return None
    def model_ready():
        return False

logger = logging.getLogger(__name__)


class MLEngine:
    """
    Machine Learning engine for stroke detection.
    
    Handles:
    - Image validation
    - Image preprocessing
    - Model inference
    - Result formatting
    """
    
    def __init__(self):
        """Initialize ML engine and load model."""
        self.model = None
        self.classes = CLASSES
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        
        if not TF_AVAILABLE:
            logger.warning("⚠️  TensorFlow not installed. Model predictions will be unavailable.")
            logger.warning("Install TensorFlow: pip install tensorflow")
            return
        
        try:
            self.model = get_model()
            if self.model:
                logger.info(f"✅ ML Engine initialized with model shape: {self.model.input_shape}")
            else:
                logger.error("❌ Failed to load model in ML Engine")
        except Exception as e:
            logger.error(f"❌ Error initializing ML Engine: {e}")
    
    
    def is_brain_ct(self, image_bytes: bytes) -> bool:
        """
        Check if uploaded file is a brain CT/MRI scan.
        
        Args:
            image_bytes: Raw image bytes from upload
            
        Returns:
            True if valid brain scan, False otherwise
        """
        # First: Check valid image format
        is_valid_format, msg = validate_image_format(image_bytes)
        if not is_valid_format:
            logger.warning(f"Invalid image format: {msg}")
            return False
        
        # Second: Check MRI-specific characteristics
        is_valid_mri, msg = validate_mri(image_bytes)
        if not is_valid_mri:
            logger.warning(f"MRI validation failed: {msg}")
            return False
        
        return True
    
    
    def predict(self, image_bytes: bytes) -> Dict:
        """
        Predict stroke from brain CT image.
        
        Args:
            image_bytes: Raw image bytes from upload
            
        Returns:
            Dict with prediction results:
            {
                "prediction": "Haemorrhagic" | "Ischemic" | "Normal",
                "confidence": 0.92,
                "probabilities": {
                    "Haemorrhagic": 0.92,
                    "Ischemic": 0.07,
                    "Normal": 0.01
                },
                "status": "Stroke detected" | "Stroke likely" | "Normal",
                "advice": "medical advice string",
                "is_confident": true/false
            }
        """
        try:
            # Check if TensorFlow is available
            if not TF_AVAILABLE:
                return {
                    "error": "TensorFlow not installed. Cannot make predictions. Run: pip install tensorflow",
                    "prediction": "Error",
                    "confidence": 0.0
                }
            
            # Check if model is loaded
            if self.model is None:
                return {
                    "error": "Model not loaded",
                    "prediction": "Error",
                    "confidence": 0.0
                }
            
            # Step 1: Validate image
            if not self.is_brain_ct(image_bytes):
                return {
                    "error": "Image does not appear to be a brain CT/MRI scan",
                    "is_brain": False,
                    "prediction": "Invalid Input"
                }
            
            # Step 2: Preprocess image
            processed_image = preprocess_image(image_bytes)
            
            # Step 3: Run inference
            predictions = self.model.predict(processed_image, verbose=0)
            prediction_scores = predictions[0]  # Remove batch dimension
            
            # Step 4: Extract results
            predicted_class_idx = np.argmax(prediction_scores)
            predicted_class = self.classes[predicted_class_idx]
            confidence = float(prediction_scores[predicted_class_idx])
            
            # Step 5: Check confidence threshold
            is_confident = confidence >= self.confidence_threshold
            
            if not is_confident:
                return {
                    "error": f"Model confidence ({confidence:.2%}) below threshold ({self.confidence_threshold:.0%})",
                    "prediction": "Low Confidence",
                    "confidence": confidence,
                    "probabilities": self._format_probabilities(prediction_scores)
                }
            
            # Step 6: Format response
            result = {
                "prediction": predicted_class,
                "confidence": confidence,
                "probabilities": self._format_probabilities(prediction_scores),
                "is_confident": is_confident,
            }
            
            # Step 7: Add medical interpretation
            result.update(self._get_medical_advice(predicted_class, confidence))
            
            logger.info(f"✅ Prediction made: {predicted_class} (conf: {confidence:.2%})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}", exc_info=True)
            return {
                "error": f"Prediction failed: {str(e)}",
                "prediction": "Error"
            }
    
    
    def _format_probabilities(self, prediction_scores: np.ndarray) -> Dict[str, float]:
        """Format prediction scores as probability dict."""
        return {
            class_name: float(score)
            for class_name, score in zip(self.classes, prediction_scores)
        }
    
    
    def _get_medical_advice(self, prediction: str, confidence: float) -> Dict:
        """
        Get medical advice based on prediction.
        
        Args:
            prediction: Predicted class
            confidence: Confidence score
            
        Returns:
            Dict with status and advice
        """
        advice_map = {
            "Haemorrhagic": {
                "status": "⚠️ Haemorrhagic Stroke Detected",
                "advice": "URGENT: Seek immediate emergency medical attention. Haemorrhagic stroke (brain bleeding) requires emergency intervention. Call emergency services immediately."
            },
            "Ischemic": {
                "status": "⚠️ Ischemic Stroke Detected",
                "advice": "URGENT: Seek immediate emergency medical attention. Ischemic stroke (blood clot) requires emergency intervention. Call emergency services immediately."
            },
            "Normal": {
                "status": "✅ No Stroke Detected",
                "advice": "Brain scan appears normal. Consult with your doctor for complete analysis and medical evaluation."
            }
        }
        
        return advice_map.get(prediction, {
            "status": "Unknown",
            "advice": "Please consult a medical professional."
        })
    
    
    def is_ready(self) -> bool:
        """Check if ML engine is ready for predictions."""
        return self.model is not None


# ============================================================
# SINGLETON INSTANCE
# ============================================================

ml_engine = MLEngine()
