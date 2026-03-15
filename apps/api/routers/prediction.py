"""
Stroke prediction endpoint router.
Integrates ML engine with API and database.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from apps.api.ml_engine import ml_engine
from apps.api.models.scan_record import ScanRecord
from apps.api.models.user import User
from apps.api.routers.auth import get_current_user
from typing import List, Optional
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
        
        # ========== STEP 4: Save to Database and Filesystem ==========
        try:
            # Save image to filesystem
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Create unique filename to avoid collisions
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp_str}_{file.filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            with open(file_path, "wb") as f:
                f.write(contents)
                
            scan_record = ScanRecord(
                user_id=str(current_user.id),
                filename=file.filename,
                image_path=f"/uploads/{unique_filename}",
                prediction_result=result,
                rehab_suggestions=suggestion,
                created_at=datetime.now()
            )
            
            await scan_record.save()
            result["scan_id"] = str(scan_record.id)
            result["image_url"] = scan_record.image_path
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


@router.get("/history")
async def get_history(current_user: User = Depends(get_current_user)) -> List[dict]:
    """
    Get prediction history for current user.
    
    Returns:
        List of scan records
    """
    try:
        records = await ScanRecord.find(ScanRecord.user_id == str(current_user.id)).sort("-created_at").to_list()
        return jsonable_encoder(records)
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")
