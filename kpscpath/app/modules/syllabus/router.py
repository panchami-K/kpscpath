from fastapi import APIRouter, Depends
from app.middleware.auth_guard import get_current_user
from app.core.response import success_response
from app.modules.syllabus import service
from app.modules.syllabus.schemas import TopicStatusUpdate

router = APIRouter(prefix="/syllabus", tags=["Syllabus"])


@router.get("/")
def list_syllabuses():
    data = service.get_all_syllabuses()
    return success_response(data=data)


@router.get("/{syllabus_id}/subjects")
def list_subjects(syllabus_id: str, user=Depends(get_current_user)):
    data = service.get_subjects_with_progress(syllabus_id, user)
    return success_response(data=data)


@router.get("/subjects/{subject_id}/topics")
def list_topics(subject_id: str, user=Depends(get_current_user)):
    data = service.get_topics_for_subject(subject_id, user)
    return success_response(data=data)


@router.patch("/topics/{topic_id}/status")
def update_status(
    topic_id: str,
    body: TopicStatusUpdate,
    user=Depends(get_current_user),
):
    data = service.update_topic_status(
        topic_id,
        user,
        body.status.value,
        body.confidence,
    )
    return success_response(data=data)


@router.get("/progress")
def progress_summary(user=Depends(get_current_user)):
    data = service.get_progress_summary(user)
    return success_response(data=data)