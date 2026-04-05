from app.core.errors import AppError
from app.core.supabase_client import service_client
from app.modules.auth.schemas import (
    RegisterRequest,
    VerifyOTPRequest,
    LoginRequest,
    ResetPasswordRequest,
)


# supabase-py v2 is synchronous — no await on any auth calls


def register(req: RegisterRequest) -> dict:
    try:
        response = service_client.auth.sign_up(
            {
                "email": req.email,
                "password": req.password,
                "options": {"data": {"full_name": req.full_name}},
            }
        )
        # sign_up returns a user even if already registered (Supabase behaviour)
        # Detect duplicate by checking identities list is empty
        if response.user and len(response.user.identities or []) == 0:
            raise AppError(AppError.EMAIL_EXISTS, "Email already registered.", 409)
        return {"message": "Account created. Check your email for the OTP."}
    except AppError:
        raise
    except Exception as e:
        raise AppError(AppError.SUPABASE_ERROR, str(e), 500)


def verify_otp(req: VerifyOTPRequest) -> dict:
    try:
        response = service_client.auth.verify_otp(
            {"email": req.email, "token": req.token, "type": "email"}
        )
        if not response.user:
            raise AppError(AppError.INVALID_OTP, "Invalid or expired OTP.", 400)
        return {"message": "Email verified successfully."}
    except AppError:
        raise
    except Exception as e:
        raise AppError(AppError.SUPABASE_ERROR, str(e), 500)


def login(req: LoginRequest) -> dict:
    try:
        response = service_client.auth.sign_in_with_password(
            {"email": req.email, "password": req.password}
        )
        if not response.user or not response.session:
            raise AppError(AppError.INVALID_CREDENTIALS, "Invalid email or password.", 401)
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": str(response.user.id),
        }
    except AppError:
        raise
    except Exception as e:
        # Supabase raises generic Exception with "Invalid login credentials"
        if "Invalid login" in str(e) or "invalid_grant" in str(e):
            raise AppError(AppError.INVALID_CREDENTIALS, "Invalid email or password.", 401)
        raise AppError(AppError.SUPABASE_ERROR, str(e), 500)


def refresh_session(refresh_token: str) -> dict:
    try:
        response = service_client.auth.refresh_session(refresh_token)
        if not response.session:
            raise AppError(AppError.UNAUTHORIZED, "Session expired. Please log in again.", 401)
        return {"access_token": response.session.access_token}
    except AppError:
        raise
    except Exception as e:
        raise AppError(AppError.UNAUTHORIZED, "Session expired. Please log in again.", 401)


def logout(access_token: str) -> dict:
    try:
        service_client.auth.admin.sign_out(access_token)
        return {"message": "Logged out successfully."}
    except Exception as e:
        # Logout should never hard-fail for the user
        return {"message": "Logged out."}


def forgot_password(email: str) -> dict:
    try:
        service_client.auth.reset_password_email(email)
        # Always return success — never reveal if email exists
        return {"message": "If that email is registered, a reset link has been sent."}
    except Exception as e:
        raise AppError(AppError.SUPABASE_ERROR, str(e), 500)