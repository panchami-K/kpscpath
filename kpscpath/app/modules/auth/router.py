from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from app.core.errors import AppError
from app.core.response import success_response, error_response
import app.modules.auth.service as service
from app.modules.auth.schemas import (
    RegisterRequest,
    VerifyOTPRequest,
    LoginRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)

REFRESH_COOKIE = "refresh_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def _set_refresh_cookie(response: JSONResponse, token: str) -> JSONResponse:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        samesite="strict",
        secure=False,   # Set True in production (HTTPS only)
        max_age=COOKIE_MAX_AGE,
        path="/",
    )
    return response


def _clear_refresh_cookie(response: JSONResponse) -> JSONResponse:
    response.delete_cookie(key=REFRESH_COOKIE, path="/")
    return response


@router.post("/register", status_code=201)
def register(req: RegisterRequest):
    try:
        data = service.register(req)
        return JSONResponse(content=success_response(data), status_code=201)
    except AppError as e:
        return JSONResponse(content=error_response(e.code, e.message), status_code=e.status_code)


@router.post("/verify", status_code=200)
def verify(req: VerifyOTPRequest):
    try:
        data = service.verify_otp(req)
        return JSONResponse(content=success_response(data))
    except AppError as e:
        return JSONResponse(content=error_response(e.code, e.message), status_code=e.status_code)


@router.post("/login", status_code=200)
def login(req: LoginRequest):
    try:
        result = service.login(req)
        response = JSONResponse(
            content=success_response(
                {
                    "access_token": result["access_token"],
                    "user_id": result["user_id"],
                }
            )
        )
        return _set_refresh_cookie(response, result["refresh_token"])
    except AppError as e:
        return JSONResponse(content=error_response(e.code, e.message), status_code=e.status_code)


@router.post("/refresh", status_code=200)
def refresh(request: Request):
    try:
        token = request.cookies.get(REFRESH_COOKIE)
        if not token:
            raise AppError(
                AppError.MISSING_REFRESH_TOKEN,
                "Refresh token missing. Please log in again.",
                401,
            )
        data = service.refresh_session(token)
        return JSONResponse(content=success_response(data))
    except AppError as e:
        return JSONResponse(content=error_response(e.code, e.message), status_code=e.status_code)


@router.post("/logout", status_code=200)
def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    try:
        access_token = credentials.credentials if credentials else None
        if access_token:
            service.logout(access_token)
        response = JSONResponse(content=success_response({"message": "Logged out successfully."}))
        return _clear_refresh_cookie(response)
    except AppError as e:
        return JSONResponse(content=error_response(e.code, e.message), status_code=e.status_code)


@router.post("/forgot", status_code=200)
def forgot_password(req: ResetPasswordRequest):
    try:
        data = service.forgot_password(req.email)
        return JSONResponse(content=success_response(data))
    except AppError as e:
        return JSONResponse(content=error_response(e.code, e.message), status_code=e.status_code)