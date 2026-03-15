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

class ChatMessage(BaseModel):
    role: str  # 'user' or 'bot'
    text: str

class ChatRequest(BaseModel):
    message: str
    current_context: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = []

@router.post("/ask")
async def ask_chatbot(request: ChatRequest, current_user: User = Depends(get_current_user)):
    if not model:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")
    
    try:
        # Fetch up to 10 past scans for better historical perspective
        past_scans = await ScanRecord.find(ScanRecord.user_id == str(current_user.id)).sort("-created_at").limit(10).to_list()
        
        history_context = ""
        if past_scans:
            history_context = "User's Past Scan History:\n"
            for scan in past_scans:
                p_res = scan.prediction_result
                date = scan.created_at.strftime("%Y-%m-%d")
                status = p_res.get('status', 'Unknown')
                pred = p_res.get('prediction', 'Unknown')
                conf = p_res.get('confidence', 0)
                history_context += f"- {date}: {status} (Prediction: {pred}, Confidence: {conf:.1%})\n"
        
        # Build chat history context
        convo_history = ""
        current_history = request.chat_history or []
        if current_history:
            convo_history = "Recent Conversation:\n"
            # Take last 6 messages
            for msg in current_history[-6:]:
                role_label = "User" if msg.role == "user" else "Assistant"
                convo_history += f"{role_label}: {msg.text}\n"

        chat_context = f"The patient is {current_user.full_name}. {history_context}"
        if request.current_context:
            chat_context += f"\nCurrently Viewied Scan Details: {request.current_context}. "
        
        prompt = (
            f"You are 'Partha-Bot', a specialized Medical Rehabilitation AI Assistant. "
            f"SYSTEM CONTEXT:\n{chat_context}\n"
            f"{convo_history}"
            f"User NEW Question: {request.message}\n\n"
            f"Instructions:\n"
            f"1. Provide empathetic and medically sound rehabilitation suggestions based on the scan history AND current chat.\n"
            f"2. Use historical scan trends if visible (e.g., if multiple 'Haemorrhagic' scans appear).\n"
            f"3. Keep responses professional, helpful, and under 3 paragraphs.\n"
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
