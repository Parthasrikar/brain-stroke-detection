from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Optional, List
from .auth import get_current_user
from apps.api.models.user import User
from apps.api.models.scan_record import ScanRecord

load_dotenv()

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Using 'gemini-flash-latest' which is verified as working in this environment
    model = genai.GenerativeModel(
        model_name='gemini-flash-latest',
        generation_config={
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 1024,
        }
    )
else:
    model = None

class ChatRequest(BaseModel):
    message: str
    current_context: Optional[str] = None

@router.post("/ask")
async def ask_chatbot(request: ChatRequest, current_user: User = Depends(get_current_user)):
    if not model:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")
    
    try:
        # Fetch up to 5 past scans for context
        past_scans = await ScanRecord.find(ScanRecord.user_id == str(current_user.id)).sort("-created_at").limit(5).to_list()
        
        history_context = ""
        if past_scans:
            history_context = "User's Past Scan History:\n"
            for scan in past_scans:
                result = scan.prediction_result.get('status', 'Unknown')
                date = scan.created_at.strftime("%Y-%m-%d")
                history_context += f"- {date}: {result}\n"
        
        chat_context = f"The user is {current_user.full_name}. {history_context}"
        if request.current_context:
            chat_context += f"\nCurrent Session Scan: {request.current_context}. "
        
        prompt = (
            f"You are a helpful Medical Rehabilitation Assistant. "
            f"Context: {chat_context}\n"
            f"User Question: {request.message}\n\n"
            f"Instructions:\n"
            f"1. Provide empathetic and medically sound rehabilitation suggestions.\n"
            f"2. Use history if relevant.\n"
            f"3. Keep it brief.\n"
            f"4. ALWAYS state: 'I am an AI assistant. Please consult your physician for final medical decisions.'\n"
        )
        
        response = model.generate_content(prompt)
        return {"response": response.text}

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            raise HTTPException(status_code=429, detail="The AI Assistant is currently busy due to high demand. Please try again in 30 seconds.")
        print(f"Chatbot Error: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Assistant Error: {error_msg}")
