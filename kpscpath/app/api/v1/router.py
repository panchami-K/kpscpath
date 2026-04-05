from fastapi import APIRouter, Depends
from app.middleware.auth_guard import get_current_user
from app.core.response import success_response
from app.modules.syllabus import service
from app.modules.syllabus.schemas import TopicStatusUpdate

router = APIRouter(prefix="/syllabus", tags=["Syllabus"])


# ─────────────────────────────────────────────────────────────
# STATIC ROUTES FIRST — must come before any dynamic /{param} routes
# ─────────────────────────────────────────────────────────────

@router.get("")          # FIX: was "/", now "" — avoids redirect issues
def list_syllabuses():
    data = service.get_all_syllabuses()
    return success_response(data=data)


@router.get("/progress")  # FIX: moved up, before /{syllabus_id}/subjects
def progress_summary(user=Depends(get_current_user)):
    data = service.get_progress_summary(user["sub"])
    return success_response(data=data)


@router.get("/subjects/{subject_id}/topics")  # FIX: moved up, before /{syllabus_id}
def list_topics(subject_id: str, user=Depends(get_current_user)):
    data = service.get_topics_for_subject(subject_id, user["sub"])
    return success_response(data=data)


@router.patch("/topics/{topic_id}/status")  # FIX: moved up, before /{syllabus_id}
def update_status(
    topic_id: str,
    body: TopicStatusUpdate,
    user=Depends(get_current_user),
):
    data = service.update_topic_status(
        topic_id,
        user["sub"],
        body.status.value,
        body.confidence,
    )
    return success_response(data=data)


# ─────────────────────────────────────────────────────────────
# DYNAMIC ROUTES LAST — /{param} catches everything, must be at the bottom
# ─────────────────────────────────────────────────────────────

@router.get("/{syllabus_id}/subjects")
def list_subjects(syllabus_id: str, user=Depends(get_current_user)):
    data = service.get_subjects_with_progress(syllabus_id, user["sub"])
    return success_response(data=data)