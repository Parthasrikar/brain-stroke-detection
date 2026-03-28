from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import uvicorn
import os
from contextlib import asynccontextmanager

from apps.api.models.user import User
from apps.api.models.scan_record import ScanRecord
from apps.api.routers import auth, prediction, chatbot


# ===============================
# Database Configuration
# ===============================

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.getenv("DB_NAME", "brain")


# ===============================
# Application Lifespan
# ===============================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    print("Connecting to MongoDB...")

    try:
        client = AsyncIOMotorClient(
            MONGO_URL,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )

        # Explicitly get the database object using the get_database method
        # This resolves "MotorDatabase is not callable" errors in some environments/versions
        db = client.get_database(DB_NAME)

        await init_beanie(
            database=db,
            document_models=[User, ScanRecord]
        )

        print(f"MongoDB connected successfully to database: {DB_NAME}")

    except Exception as e:
        print("MongoDB connection error:", e)

    yield
    print("Application shutdown.")


# ===============================
# FastAPI App
# ===============================

app = FastAPI(
    title="Brain Stroke Detection API",
    description="API for Brain Stroke Detection and Rehabilitation Support",
    version="1.0.0",
    lifespan=lifespan
)


# ===============================
# CORS Configuration
# ===============================

origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:80,https://frontend-production-8d4a.up.railway.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================
# Routers
# ===============================

app.include_router(auth.router)
app.include_router(prediction.router)
app.include_router(chatbot.router)


# ===============================
# Static Upload Folder
# ===============================

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ===============================
# Routes
# ===============================

@app.get("/")
async def root():
    return {"message": "Welcome to Brain Stroke Detection API. Models loaded."}


@app.get("/health")
async def health():
    return {"status": "ok"}


# ===============================
# Local Development Run
# ===============================

if __name__ == "__main__":
    uvicorn.run(
        "apps.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )