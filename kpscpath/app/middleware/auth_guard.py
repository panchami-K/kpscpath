from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from app.core.errors import AppError
from app.core.supabase_client import anon_client

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """
    FastAPI dependency. Validates the Bearer token via Supabase Auth.
    Returns user_id as string. Raises AppError UNAUTHORIZED if invalid.

    Usage in a route:
        @router.get("/me")
        def get_me(user_id: str = Depends(get_current_user)):
            ...
    """
    try:
        if not credentials or not credentials.credentials:
            raise AppError(AppError.UNAUTHORIZED, "Authorization token missing.", 401)

        token = credentials.credentials
        response = anon_client.auth.get_user(token)

        if not response.user:
            raise AppError(AppError.UNAUTHORIZED, "Invalid or expired token.", 401)

        return str(response.user.id)

    except AppError:
        raise
    except Exception as e:
        raise AppError(AppError.UNAUTHORIZED, "Invalid or expired token.", 401)