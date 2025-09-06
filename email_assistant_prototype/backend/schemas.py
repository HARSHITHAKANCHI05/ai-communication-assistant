
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class EmailOut(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    received_at: Optional[datetime]
    filtered: int
    sentiment: str
    sentiment_score: Optional[int]
    priority: str
    priority_score: Optional[int]
    extracted: Optional[Any]
    draft: Optional[str]
    status: str

    class Config:
        orm_mode = True
