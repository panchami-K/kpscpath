from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.core.errors import AppError
from app.core.response import success_response, error_response
from app.middleware.auth_guard import get_current_user
from app.modules.onboarding.schemas import OnboardingRequest
import app.modules.onboarding.service as service

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/exam-dates", status_code=200)
def get_exam_dates(
    exam_type: str = Query(
        default=None,
        description="Filter by exam type: KAS, FDA, SDA, PSI, KES. Leave empty for all."
    )
):
    """
    Returns available exam date options — confirmed and predicted.
    No auth required. Used on the onboarding screen before user selects exam.

    Response groups options by exam type with labels in both Kannada and English.
    Predicted dates include a note explaining the prediction basis.
    When official dates are announced, is_confirmed becomes true automatically.
    """
    try:
        if exam_type:
            exam_type = exam_type.upper()
            data = {exam_type: service.get_exam_date_options(exam_type)}
        else:
            data = service.get_all_exam_options()

        return JSONResponse(content=success_response(data))
    except AppError as e:
        return JSONResponse(
            content=error_response(e.code, e.message),
            status_code=e.status_code,
        )


@router.post("/complete", status_code=200)
def complete_onboarding(
    req: OnboardingRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Called once after registration. Saves:
    - target_exam: KAS, FDA, SDA, PSI, KES, or other
    - exam_date: user-selected target date (from exam-dates options or custom)
    - study_slots: list of daily time ranges e.g. [{"from_time":"06:00","to_time":"08:00"}]
    - preferred_lang: kn (Kannada) or en (English)

    Calculates total daily study minutes from slots.
    Sets onboarding_done = true.

    Requires: Authorization: Bearer <access_token>
    """
    try:
        data = service.complete_onboarding(user_id, req)
        return JSONResponse(content=success_response(data))
    except AppError as e:
        return JSONResponse(
            content=error_response(e.code, e.message),
            status_code=e.status_code,
        )


@router.get("/profile", status_code=200)
def get_profile(user_id: str = Depends(get_current_user)):
    """
    Returns current user profile.
    Frontend uses this to decide:
    - onboarding_done = false → show onboarding screen
    - onboarding_done = true  → show dashboard

    Requires: Authorization: Bearer <access_token>
    """
    try:
        data = service.get_profile(user_id)
        return JSONResponse(content=success_response(data))
    except AppError as e:
        return JSONResponse(
            content=error_response(e.code, e.message),
            status_code=e.status_code,
        )