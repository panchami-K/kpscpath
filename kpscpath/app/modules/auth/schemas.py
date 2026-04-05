from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ConfirmResetRequest(BaseModel):
    new_password: str = Field(..., min_length=8)