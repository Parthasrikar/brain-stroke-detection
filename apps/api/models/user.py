from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime

class User(Document):
    email: EmailStr
    password_hash: str
    full_name: str
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"
