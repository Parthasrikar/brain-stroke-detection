# 🔧 STEP-BY-STEP IMPLEMENTATION GUIDE: Hybrid Integration

## 📋 Overview

This guide walks through the **exact commands and code changes** to integrate mega-project ML code into m-project/apps using the **Hybrid Approach**.

**Estimated Time:** 3-4 hours  
**Difficulty:** Medium  
**Prerequisites:** Both projects set up, Python knowledge  

---

## ⚙️ PHASE 1: ENVIRONMENT SETUP (15 minutes)

### Step 1.1: Verify Current Directory Structure

```bash
# Navigate to m-project
cd /Users/gparthasrikar/Documents/m-project

# Verify structure
tree -L 2 -I '__pycache__|*.pyc'
# Should show:
# ├── apps/
# │   ├── api/
# │   ├── web/
# ├── mega-project/
# ├── Brain_Stroke_CT_Dataset/
# └── PROJECT_DOCUMENTATION.*
```

### Step 1.2: Create Backup

```bash
# Backup the current api directory (CRITICAL)
cp -r apps/api apps/api.backup

# Verify backup
ls -la apps/ | grep backup
```

### Step 1.3: Create AI Module Directory

```bash
# Create the new AI module structure
mkdir -p apps/ai/models
mkdir -p apps/ai/preprocessing

# Create __init__ files to make them packages
touch apps/ai/__init__.py
touch apps/ai/preprocessing/__init__.py

# Verify structure
tree apps/ai/
# Should show:
# apps/ai/
# ├── __init__.py
# ├── models/
# └── preprocessing/
#     └── __init__.py
```

### Step 1.4: Copy the Model File

```bash
# Copy the trained ResNet50 ensemble model (200MB) ⚠️ This will take ~30 seconds
cp mega-project/stroke_model_resnet50_ensemble.h5 apps/ai/models/

# Verify file integrity
ls -lh apps/ai/models/stroke_model_resnet50_ensemble.h5
# Should show size around 200M

# Quick check: file is readable
file apps/ai/models/stroke_model_resnet50_ensemble.h5
# Should show: "data" (binary model file)
```

---

## 🔍 PHASE 2: EXTRACT PREPROCESSING FUNCTIONS (45 minutes)

### Step 2.1: Read Source File

Open and read the mega-project Flask app to identify functions to extract:

```bash
head -200 mega-project/app.py
```

Look for these key sections:
- `preprocess_image(image)` - around line 70-80
- `validate_mri(image)` - around line 100-140
- Constants like `IMG_SIZE`, `CLASSES`, `CONFIDENCE_THRESHOLD`

### Step 2.2: Create Preprocessing Module

Create a new file: `apps/ai/preprocessing/image_processing.py`

```python
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

def validate_mri(image_bytes: bytes) -> tuple[bool, str]:
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


def validate_image_format(image_bytes: bytes) -> tuple[bool, str]:
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
```

### Step 2.3: Create Model Loading Module

Create: `apps/ai/model_loader.py`

```python
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
        return env_path
    
    # Check default location
    default_paths = [
        "apps/ai/models/stroke_model_resnet50_ensemble.h5",
        "/Users/gparthasrikar/Documents/m-project/apps/ai/models/stroke_model_resnet50_ensemble.h5",
    ]
    
    for path in default_paths:
        if os.path.exists(path):
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
```

### Step 2.4: Update Preprocessing __init__.py

Edit: `apps/ai/preprocessing/__init__.py`

```python
"""
AI/ML preprocessing module for brain stroke detection.
"""

from .image_processing import (
    preprocess_image,
    validate_mri,
    validate_image_format,
    IMG_SIZE,
    CLASSES,
    CONFIDENCE_THRESHOLD,
)

__all__ = [
    "preprocess_image",
    "validate_mri",
    "validate_image_format",
    "IMG_SIZE",
    "CLASSES",
    "CONFIDENCE_THRESHOLD",
]
```

---

## 🧠 PHASE 3: UPDATE ML ENGINE (45 minutes)

### Step 3.1: Read Current ml_engine.py

```bash
cat apps/api/ml_engine.py
```

Note what's currently there (placeholder, basic logic, etc.)

### Step 3.2: Create Enhanced ML Engine

Replace/Update: `apps/api/ml_engine.py`

```python
"""
ML Engine for brain stroke detection.
Integrates TensorFlow model with preprocessing and validation.
"""

import numpy as np
import logging
from typing import Dict, List, Optional
import tensorflow as tf
from io import BytesIO
from PIL import Image

# Import our preprocessing module
from apps.ai.preprocessing import (
    preprocess_image,
    validate_mri,
    validate_image_format,
    CLASSES,
    CONFIDENCE_THRESHOLD,
)
from apps.ai.model_loader import get_model, model_ready

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
```

### Step 3.3: Update API Requirements

Edit: `apps/api/requirements.txt`

Add these lines (keep existing ones):

```
tensorflow>=2.16.0
tensorflow-hub>=0.17.0
numpy>=1.24.0
pillow>=10.0.0
scikit-learn>=1.3.0
monai>=1.3.0
google-generativeai>=0.3.0
```

---

## 🔌 PHASE 4: UPDATE PREDICTION ROUTER (30 minutes)

### Step 4.1: Read Current Router

```bash
cat apps/api/routers/prediction.py
```

### Step 4.2: Update Prediction Router

Edit/Replace: `apps/api/routers/prediction.py`

```python
"""
Stroke prediction endpoint router.
Integrates ML engine with API and database.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from apps.api.ml_engine import ml_engine
from apps.api.models.scan_record import ScanRecord
from apps.api.models.user import User
from apps.api.routers.auth import get_current_user
from typing import Optional
import os
import logging
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/predict", tags=["Prediction"])
logger = logging.getLogger(__name__)

# Gemini setup for automated suggestions
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
else:
    gemini_model = None
    logger.warning("GEMINI_API_KEY not set. AI-generated suggestions disabled.")


@router.post("/")
async def predict_stroke(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Predict stroke from brain CT/MRI scan image.
    
    API Endpoint: POST /predict/
    
    Authentication: Required (JWT token)
    
    Args:
        file: Image file (CT/MRI brain scan)
        current_user: Authenticated user
        
    Returns:
        {
            "prediction": "Haemorrhagic" | "Ischemic" | "Normal",
            "confidence": 0.92,
            "probabilities": {...},
            "status": "Stroke detected",
            "advice": "medical advice",
            "suggestion": "AI-generated suggestion",
            "scan_id": "mongodb_id",
            "saved_to_db": true
        }
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="❌ File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read file bytes
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="❌ Empty file uploaded")
        
        logger.info(f"Processing prediction for user {current_user.id}")
        
        # ========== STEP 1: Validate MRI ==========
        if not ml_engine.is_brain_ct(contents):
            logger.warning(f"Invalid brain scan from user {current_user.id}")
            return {
                "error": "The uploaded image does not appear to be a Brain CT/MRI scan. Please upload a valid medical scan.",
                "is_brain": False,
                "prediction": "Invalid Input"
            }
        
        # ========== STEP 2: Run Prediction ==========
        result = ml_engine.predict(contents)
        
        # Check for errors
        if "error" in result and result.get("prediction") == "Error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        # ========== STEP 3: Get AI Suggestions (Optional) ==========
        suggestion = "Consult a medical professional for complete diagnosis."
        
        if gemini_model and "status" in result:
            try:
                prompt = f"""
                Patient Brain Scan Analysis:
                - Prediction: {result['prediction']}
                - Confidence: {result['confidence']:.1%}
                - Status: {result.get('status', 'Unknown')}
                
                Provide 3 specific medical rehabilitation or next-step recommendations.
                Keep response brief and practical.
                """
                
                response = gemini_model.generate_content(prompt)
                suggestion = response.text
                
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Continue without suggestion
        
        result["suggestion"] = suggestion
        
        # ========== STEP 4: Save to Database ==========
        try:
            scan_record = ScanRecord(
                user_id=current_user.id,
                prediction=result["prediction"],
                confidence=result["confidence"],
                probabilities=result["probabilities"],
                timestamp=datetime.now(),
                model_version="resnet50_ensemble_v1"
            )
            
            await scan_record.save()
            result["scan_id"] = str(scan_record.id)
            result["saved_to_db"] = True
            
            logger.info(f"✅ Scan saved to DB: {scan_record.id}")
            
        except Exception as e:
            logger.error(f"Database save error: {e}")
            result["saved_to_db"] = False
            # Continue without saving
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in predict: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/health")
async def health_check() -> dict:
    """
    Health check for prediction service.
    
    Returns:
        {
            "model_loaded": true,
            "ready": true,
            "version": "1.0.0"
        }
    """
    return {
        "model_loaded": ml_engine.is_ready(),
        "ready": ml_engine.is_ready(),
        "version": "1.0.0",
        "classes": ml_engine.classes
    }
```

---

## 🧪 PHASE 5: TESTING (20 minutes)

### Step 5.1: Setup Environment Variables

Create/Update: `.env` in `apps/api/`

```bash
# Backend Configuration
DATABASE_URL=mongodb://localhost:27017
DB_NAME=brain_stroke_db
FLASK_ENV=development

# Model Configuration
MODEL_PATH=/Users/gparthasrikar/Documents/m-project/apps/ai/models/stroke_model_resnet50_ensemble.h5

# API Configuration  
FRONTEND_URL=http://localhost:5173

# Gemini API (optional)
GEMINI_API_KEY=your_api_key_here
```

### Step 5.2: Install Dependencies

```bash
# Navigate to apps/api
cd /Users/gparthasrikar/Documents/m-project/apps/api

# Install/upgrade dependencies
pip install -r requirements.txt

# Verify TensorFlow installation
python -c "import tensorflow as tf; print(f'TensorFlow version: {tf.__version__}')"
```

### Step 5.3: Test Model Loading

```bash
python -c "
from apps.ai.model_loader import get_model
model = get_model()
if model:
    print(f'✅ Model loaded successfully!')
    print(f'Input shape: {model.input_shape}')
else:
    print('❌ Model failed to load')
"
```

### Step 5.4: Start Backend Server

```bash
# From apps/api directory
uvicorn main:app --reload --port 8000

# In another terminal, test health check
curl http://localhost:8000/predict/health

# Expected response:
# {
#   "model_loaded": true,
#   "ready": true,
#   "version": "1.0.0",
#   "classes": ["Haemorrhagic", "Ischemic", "Normal"]
# }
```

### Step 5.5: Test with Sample Image

```bash
# Get a test image from mega-project
TEST_IMAGE="/Users/gparthasrikar/Documents/m-project/mega-project/Brain_Stroke_CT_Dataset/Normal/DICOM/10002.dcm"

# Or use a PNG if available
# This requires a valid brain scan image

# Test endpoint (with authentication token)
curl -X POST http://localhost:8000/predict/ \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -F "file=@/path/to/test_image.jpg"

# Expected response:
# {
#   "prediction": "Normal",
#   "confidence": 0.92,
#   "probabilities": {...},
#   "status": "✅ No Stroke Detected",
#   "advice": "Brain scan appears normal...",
#   "scan_id": "mongodb_id",
#   "saved_to_db": true
# }
```

---

## 🎨 PHASE 6: FRONTEND INTEGRATION (30 minutes)

### Step 6.1: Update API Configuration

Edit: `apps/web/src/api.js` (or create if doesn't exist)

```javascript
/**
 * API Client for Brain Stroke Detection
 * Connects to FastAPI backend on port 8000
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = {
  /**
   * Upload image for stroke prediction
   */
  predict: async (file, token) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/predict/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Prediction failed');
    }
    
    return await response.json();
  },
  
  /**
   * Check API health
   */
  health: async () => {
    const response = await fetch(`${API_BASE_URL}/predict/health`);
    return await response.json();
  }
};
```

### Step 6.2: Update Components

Edit: `apps/web/src/components/Upload.jsx` (or create relevant component)

```javascript
import { useState } from 'react';
import { apiClient } from '../api';

export default function Upload({ onResult, currentUser }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleUpload = async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      // Get JWT token from localStorage or auth context
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('Not authenticated. Please log in first.');
      }
      
      // Call API
      const result = await apiClient.predict(file, token);
      
      // Handle different response types
      if (result.error && result.prediction === 'Invalid Input') {
        setError(result.error || 'Invalid image. Please upload a brain CT/MRI scan.');
        onResult(null);
      } else if (result.error) {
        setError(result.error);
        onResult(null);
      } else {
        oncResult(result);
      }
      
    } catch (err) {
      setError(err.message || 'Prediction failed');
      onResult(null);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="upload-container">
      <input
        type="file"
        accept="image/*"
        onChange={(e) => e.target.files[0] && handleUpload(e.target.files[0])}
        disabled={loading}
      />
      
      {loading && <p>🔄 Processing image...</p>}
      {error && <p className="error">⚠️ {error}</p>}
    </div>
  );
}
```

---

## ✅ VALIDATION CHECKLIST

After completing all phases:

```bash
# 1. Model file exists
ls -lh apps/ai/models/stroke_model_resnet50_ensemble.h5

# 2. Preprocessing module works
python -c "from apps.ai.preprocessing import preprocess_image, validate_mri; print('✅ Imports work')"

# 3. Model loader works
python -c "from apps.ai.model_loader import get_model; print(f'Model: {get_model() is not None}')"

# 4. ML engine initializes
python -c "from apps.api.ml_engine import ml_engine; print(f'ML Ready: {ml_engine.is_ready()}')"

# 5. Start server and test
cd apps/api
uvicorn main:app --reload

# In another terminal:
curl http://localhost:8000/predict/health
```

---

## 🚀 FINAL CHECKLIST

- [ ] Model file copied (200MB)
- [ ] Preprocessing module created
- [ ] Model loader created  
- [ ] ML engine updated
- [ ] Prediction router updated
- [ ] Requirements.txt updated
- [ ] Environment variables set
- [ ] Backend starts without errors
- [ ] Health check endpoint works
- [ ] Frontend API updated
- [ ] End-to-end test successful

**Estimated time: 3-4 hours**

