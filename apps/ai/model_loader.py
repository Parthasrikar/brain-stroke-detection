"""
TensorFlow model loading and caching for brain stroke detection.
"""

import os
import tensorflow as tf
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================
# GLOBAL MODEL CACHE
# ============================================================

_model_cache = None
_model_path = None


def get_model_path() -> str:
    """
    Get the path to the trained model file.
    
    Checks in order:
    1. Environment variable MODEL_PATH
    2. apps/ai/models/stroke_model_resnet50_ensemble.h5
    3. Raises error if not found
    """
    # Check environment variable first
    env_path = os.getenv("MODEL_PATH")
    if env_path and os.path.exists(env_path):
        logger.info(f"Using MODEL_PATH from environment: {env_path}")
        return env_path
    
    # Check default locations
    default_paths = [
        "apps/ai/models/stroke_model_resnet50_ensemble.h5",
        "/Users/gparthasrikar/Documents/m-project/apps/ai/models/stroke_model_resnet50_ensemble.h5",
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            logger.info(f"Found model at: {path}")
            return path
    
    raise FileNotFoundError(
        f"Model file not found. Checked: {default_paths}\n"
        f"Set MODEL_PATH environment variable or place model in apps/ai/models/"
    )


def load_model() -> tf.keras.Model:
    """
    Load TensorFlow model with error handling.
    
    Returns:
        Loaded Keras model or None if failed
    """
    global _model_cache, _model_path
    
    # Return cached model if already loaded
    if _model_cache is not None:
        logger.info("Returning cached model")
        return _model_cache
    
    try:
        model_path = get_model_path()
        _model_path = model_path
        
        logger.info(f"Loading model from: {model_path}")
        model = tf.keras.models.load_model(model_path)
        
        # Cache the model
        _model_cache = model
        
        logger.info(f"✅ Model loaded successfully. Shape: {model.input_shape}")
        return model
        
    except FileNotFoundError as e:
        logger.error(f"❌ Model file not found: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Error loading model: {type(e).__name__} - {str(e)}")
        return None


def get_model() -> tf.keras.Model:
    """
    Get the cached model. Load if not already loaded.
    
    Returns:
        Loaded Keras model
        
    Raises:
        RuntimeError: If model cannot be loaded
    """
    global _model_cache
    
    if _model_cache is None:
        _model_cache = load_model()
    
    if _model_cache is None:
        raise RuntimeError("Failed to load model. Check logs for details.")
    
    return _model_cache


def model_ready() -> bool:
    """Check if model is loaded and ready."""
    return _model_cache is not None
