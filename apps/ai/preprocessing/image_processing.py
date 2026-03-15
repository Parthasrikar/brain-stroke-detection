"""
Image preprocessing and validation for brain stroke detection.
Extracted from mega-project/app.py with enhancements.
"""

import numpy as np
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION CONSTANTS
# ============================================================

IMG_SIZE = (224, 224)
CLASSES = ["Haemorrhagic", "Ischemic", "Normal"]

# ⭐ TIER 1 IMPROVEMENT: Confidence threshold for medical safety
# Only make predictions when model is sufficiently confident
CONFIDENCE_THRESHOLD = 0.65  # 65% confidence minimum for prediction


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess image for model inference.
    
    Args:
        image_bytes: Raw image bytes from upload
        
    Returns:
        Preprocessed image array [1, 224, 224, 3] ready for inference
        
    Raises:
        ValueError: If image is invalid or cannot be processed
    """
    try:
        # Load image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB (handle RGBA, grayscale, etc.)
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Resize to model input size
        image = image.resize(IMG_SIZE, Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize [0-1]
        image_array = np.array(image) / 255.0
        
        # Add batch dimension [1, H, W, C]
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise ValueError(f"Failed to preprocess image: {str(e)}")


# ============================================================
# MRI VALIDATION (Out-of-Distribution Detection)
# ============================================================

def validate_mri(image_bytes: bytes) -> tuple:
    """
    Validate if uploaded image is likely a brain MRI/CT scan.
    
    This prevents model from making predictions on random images.
    Uses heuristics:
    1. Image dimensions (must be square-ish)
    2. Saturation level (MRIs are grayscale)
    3. Contrast levels (medical images have specific patterns)
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        (is_valid: bool, message: str)
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # ========== CHECK 1: Image Size ==========
        width, height = image.size
        
        if width < 50 or height < 50:
            return False, "❌ Image is too small. Minimum size: 50x50 pixels."
        
        if width > 4096 or height > 4096:
            return False, "❌ Image is too large. Maximum size: 4096x4096 pixels."
        
        # ========== CHECK 2: Aspect Ratio ==========
        aspect_ratio = max(width, height) / min(width, height)
        
        if aspect_ratio > 1.5:
            return False, "❌ Image aspect ratio is too extreme. MRI scans are typically square-like."
        
        # ========== CHECK 3: Saturation (Grayscale Check) ==========
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Convert to HSV to check saturation
        hsv_image = image.convert('HSV')
        h, s, v = hsv_image.split()
        avg_saturation = np.mean(np.array(s))
        
        # MRI images are grayscale (low saturation)
        # Threshold: 0-255, normal for color images ~100+, MRI ~30-50
        if avg_saturation > 100:
            return False, "❌ Image appears to be a color photograph, not a medical scan."
        
        # ========== CHECK 4: Contrast Levels ==========
        rgb_array = np.array(image)
        
        # Calculate standard deviation of pixel values
        std_dev = np.std(rgb_array)
        
        # MRI scans have significant contrast
        if std_dev < 10:
            return False, "❌ Image has too low contrast. This may not be a medical scan."
        
        # ========== CHECK 5: Value Range ==========
        # MRI scans use full dynamic range
        value_array = np.array(v)  # V channel from HSV
        min_val = np.min(value_array)
        max_val = np.max(value_array)
        
        value_range = max_val - min_val
        
        if value_range < 50:
            return False, "❌ Image has insufficient dynamic range for a medical scan."
        
        # ✅ All checks passed
        return True, "✅ Image appears to be a valid brain scan."
        
    except Exception as e:
        logger.error(f"Error validating MRI: {e}")
        return False, f"❌ Error validating image: {str(e)}"


def validate_image_format(image_bytes: bytes) -> tuple:
    """
    Quick validation: is this a valid image format?
    
    Args:
        image_bytes: Raw bytes to check
        
    Returns:
        (is_valid: bool, message: str)
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        return True, "✅ Valid image format"
    except Exception as e:
        return False, f"❌ Invalid image format: {str(e)}"
