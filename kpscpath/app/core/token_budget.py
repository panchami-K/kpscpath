from datetime import date
from app.core.errors import AppError

_budget: dict = {}


def check_budget(user_id: str) -> None:
    key = f"{user_id}:{date.today()}"
    if _budget.get(key, 0) >= 20:
        raise AppError(
            "RATE_LIMIT_EXCEEDED",
            429,
            "Daily AI limit reached. Resets at midnight.",
        )


def increment_budget(user_id: str) -> None:
    key = f"{user_id}:{date.today()}"
    _budget[key] = _budget.get(key, 0) + 1