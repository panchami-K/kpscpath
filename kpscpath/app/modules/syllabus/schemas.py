from pydantic import BaseModel
from typing import Optional
from enum import Enum


class TopicStatus(str, Enum):
    not_started  = "not_started"
    in_progress  = "in_progress"
    completed    = "completed"
    needs_revision = "needs_revision"


class SyllabusOut(BaseModel):
    id: str
    exam_type: str
    version: str
    description: Optional[str]
    is_active: bool


class SubjectOut(BaseModel):
    id: str
    syllabus_id: str
    name_en: str
    name_kn: str
    sort_order: int
    agent_type: Optional[str]
    total_topics: int = 0
    completed_topics: int = 0
    progress_pct: float = 0.0


class TopicOut(BaseModel):
    id: str
    subject_id: str
    name_en: str
    name_kn: str
    difficulty: Optional[str]
    importance: Optional[str]
    sort_order: int
    pyq_frequency: int = 0
    status: TopicStatus = TopicStatus.not_started
    confidence: Optional[int] = None


class TopicStatusUpdate(BaseModel):
    status: TopicStatus
    confidence: Optional[int] = None  # 1-5


class ProgressSummary(BaseModel):
    total_topics: int
    completed_topics: int
    in_progress_topics: int
    needs_revision_topics: int
    overall_pct: float
    by_subject: list