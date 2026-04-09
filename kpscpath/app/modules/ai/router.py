from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.middleware.auth_guard import get_current_user
from app.core.response import success_response
from app.modules.ai import service
from app.modules.ai.schemas import DoubtRequest, DoubtHistoryItem

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/doubt")
def ask_doubt(
    request: DoubtRequest,
    user_id: str = Depends(get_current_user),
):
    return StreamingResponse(
        service.stream_doubt_answer(request, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/doubt/history")
def doubt_history(user_id: str = Depends(get_current_user)):
    data = service.get_doubt_history(user_id)
    return success_response(data=data)