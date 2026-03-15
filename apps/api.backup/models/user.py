from beanie import Document
from pydantic import EmailStr
from datetime import datetime

class User(Document):
    email: EmailStr
    password_hash: str
    full_name: str
    created_at: datetime = datetime.now()

    class Settings:
        name = "users"
