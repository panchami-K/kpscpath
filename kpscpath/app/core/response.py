from datetime import datetime, timezone


def success_response(data: dict, meta: dict = None) -> dict:
    return {
        "success": True,
        "data": data,
        "meta": meta or {"timestamp": datetime.now(timezone.utc).isoformat()},
    }


def error_response(code: str, message: str) -> dict:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }