from beanie import Document, Link
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any
from .user import User

class ScanRecord(Document):
    user_id: str  # We'll store the User's ID as a string for simplicity or use Link[User]
    filename: str
    prediction_result: Dict[str, Any]
    rehab_suggestions: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "scan_records"
