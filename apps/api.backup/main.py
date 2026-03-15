from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import uvicorn
from contextlib import asynccontextmanager

from apps.api.models.user import User
from apps.api.models.scan_record import ScanRecord
from apps.api.routers import auth, prediction, chatbot

# Database Config (Move to config later if needed)
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "brain_stroke_db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = AsyncIOMotorClient(MONGO_URL)
    await init_beanie(database=client[DB_NAME], document_models=[User, ScanRecord])
    print("Database connected.")
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Brain Stroke Detection API",
    description="API for Brain Stroke Detection and Rehabilitation Support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(prediction.router)
app.include_router(chatbot.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Brain Stroke Detection API. Models loaded."}

if __name__ == "__main__":
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
