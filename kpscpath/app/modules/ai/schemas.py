from pydantic import BaseModel, Field
from typing import Optional


class DoubtRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)
    language: str = Field(default="kn", pattern="^(kn|en)$")
    topic_id: Optional[str] = None


class DoubtHistoryItem(BaseModel):
    id: str
    question: str
    answer: str
    language: str
    model_used: str
    created_at: str