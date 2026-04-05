from datetime import date, datetime, timezone
from app.core.errors import AppError
from app.core.supabase_client import service_client
from app.modules.onboarding.schemas import OnboardingRequest, build_display_label


def complete_onboarding(user_id: str, req: OnboardingRequest) -> dict:
    try:
        slots_json = [
            {"from_time": s.from_time, "to_time": s.to_time}
            for s in req.study_slots
        ]
        update_payload = {
            "target_exam": req.target_exam,
            "exam_date": req.exam_date.isoformat(),
            "study_slots": slots_json,
            "daily_study_mins": req.total_daily_mins,
            "preferred_lang": req.preferred_lang,
            "onboarding_done": True,
            "last_active_at": datetime.now(timezone.utc).isoformat(),
        }
        response = (
            service_client.table("users")
            .update(update_payload)
            .eq("id", user_id)
            .execute()
        )
        if not response.data:
            raise AppError(AppError.USER_NOT_FOUND, "User not found.", 404)

        days_until_exam = (req.exam_date - date.today()).days
        return {
            "user_id": user_id,
            "target_exam": req.target_exam,
            "exam_date": req.exam_date.isoformat(),
            "study_slots": [s.display_label() for s in req.study_slots],
            "study_slots_raw": slots_json,
            "total_daily_mins": req.total_daily_mins,
            "preferred_lang": req.preferred_lang,
            "days_until_exam": days_until_exam,
            "onboarding_done": True,
            "message": (
                "ಆನ್‌ಬೋರ್ಡಿಂಗ್ ಪೂರ್ಣಗೊಂಡಿದೆ! ನಿಮ್ಮ ಅಧ್ಯಯನ ಯಾತ್ರೆ ಪ್ರಾರಂಭವಾಗಿದೆ."
                if req.preferred_lang == "kn"
                else "Onboarding complete! Your study journey begins now."
            ),
        }
    except AppError:
        raise
    except Exception as e:
        raise AppError(AppError.SUPABASE_ERROR, str(e), 500)


def get_all_exam_options() -> dict:
    """
    Returns exam date options grouped by exam type.
    BUG FIX: Only skip rows where exam_date IS NOT NULL and is in the past.
    Rows with exam_date = NULL (predicted month/year) are always shown.
    """
    try:
        current_year = date.today().year
        response = (
            service_client.table("exam_date_options")
            .select("*")
            .gte("exam_year", current_year)
            .lte("exam_year", current_year + 3)
            .order("exam_year")
            .order("exam_month")
            .execute()
        )

        grouped: dict[str, list] = {}
        for row in (response.data or []):
            # Only skip if we have a confirmed exact date that's already passed
            if row.get("exam_date") and row["exam_date"] is not None:
                try:
                    exam_d = date.fromisoformat(str(row["exam_date"]))
                    if exam_d < date.today():
                        continue  # Past confirmed date — skip it
                except (ValueError, TypeError):
                    pass  # If date parsing fails, include the row

            label_en, label_kn = build_display_label(row)
            option = {
                "id": row["id"],
                "exam_type": row["exam_type"],
                "stage": row["stage"],
                "exam_date": str(row["exam_date"]) if row.get("exam_date") else None,
                "exam_month": row.get("exam_month"),
                "exam_year": row["exam_year"],
                "is_confirmed": row["is_confirmed"],
                "is_predicted": row["is_predicted"],
                "prediction_note_kn": row.get("prediction_note_kn"),
                "prediction_note_en": row.get("prediction_note_en"),
                "display_label": label_en,
                "display_label_kn": label_kn,
            }
            grouped.setdefault(row["exam_type"], []).append(option)

        return grouped
    except Exception as e:
        raise AppError(AppError.SUPABASE_ERROR, str(e), 500)


def get_exam_date_options(exam_type: str) -> list[dict]:
    """Returns exam date options for a single exam type."""
    try:
        all_options = get_all_exam_options()
        return all_options.get(exam_type.upper(), [])
    except AppError:
        raise


def get_profile(user_id: str) -> dict:
    try:
        response = (
            service_client.table("users")
            .select(
                "id, email, full_name, target_exam, exam_date, "
                "study_slots, daily_study_mins, preferred_lang, "
                "onboarding_done, plan_tier, created_at"
            )
            .eq("id", user_id)
            .single()
            .execute()
        )
        if not response.data:
            raise AppError(AppError.USER_NOT_FOUND, "User profile not found.", 404)

        profile = response.data
        days_until_exam = None
        if profile.get("exam_date"):
            try:
                exam_date = date.fromisoformat(str(profile["exam_date"]))
                days_until_exam = (exam_date - date.today()).days
            except (ValueError, TypeError):
                pass
        return {**profile, "days_until_exam": days_until_exam}
    except AppError:
        raise
    except Exception as e:
        raise AppError(AppError.SUPABASE_ERROR, str(e), 500)