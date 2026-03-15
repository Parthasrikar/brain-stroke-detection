from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from apps.api.ml_engine import ml_engine
from apps.api.models.scan_record import ScanRecord
from apps.api.models.user import User
from .auth import get_current_user
from typing import List
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/predict", tags=["Prediction"])

# Gemini setup for automated suggestions if needed
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-flash-latest')
else:
    gemini_model = None

@router.post("/")
async def predict_stroke(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    
    # 1. Check if it's a Brain CT
    if not ml_engine.is_brain_ct(contents):
        return {
            "error": "Personalization Alert: The uploaded image does not appear to be a Brain CT scan. Please upload a valid CT scan for accurate results.",
            "is_brain": False
        }

    try:
        # 2. Run inference
        result = ml_engine.predict(contents)
        
        # 3. Get Gemini Suggestions (if possible)
        rehab_suggestions = "Consult a doctor for rehabilitation plans."
        if gemini_model and "status" in result:
            try:
                prompt = f"Patient Scan Result: {result['status']}. Advice given: {result['advice']}. Provide 3 specific rehabilitation steps or suggestions for this condition."
                response = gemini_model.generate_content(prompt)
                rehab_suggestions = response.text
            except:
                pass
        
        # 4. Save to History
        record = ScanRecord(
            user_id=str(current_user.id),
            filename=file.filename,
            prediction_result=result,
            rehab_suggestions=rehab_suggestions
        )
        await record.insert()
        
        return {
            "result": result,
            "rehab_suggestions": rehab_suggestions,
            "record_id": str(record.id),
            "is_brain": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[ScanRecord])
async def get_history(current_user: User = Depends(get_current_user)):
    records = await ScanRecord.find(ScanRecord.user_id == str(current_user.id)).sort("-created_at").to_list()
    return records
