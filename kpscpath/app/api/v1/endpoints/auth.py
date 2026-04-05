from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets
import os
from dotenv import load_dotenv
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Email config (from .env)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@kpscpath.com")

async def send_real_email(email: str, otp: str):
    """Send REAL email with OTP"""
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = email
    msg['Subject'] = "🔐 KPSCPath - Your Verification Code"
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #007bff;">Welcome to KPSCPath! 🔐</h2>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
            <h1 style="font-size: 36px; color: #007bff; margin: 0;">{otp}</h1>
            <p style="color: #666; font-size: 16px;">Your verification code</p>
        </div>
        <p style="color: #555;">
            This code expires in <strong>10 minutes</strong>. Enter it to verify your account.
        </p>
        <hr style="border: none; border-top: 1px solid #eee;">
        <p style="color: #888; font-size: 14px;">
            If you didn't request this, please ignore this email.
        </p>
        <p style="color: #007bff;">
            <strong>KPSCPath Team</strong>
        </p>
    </div>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        use_tls=True
    )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.services.auth_service import (
    create_user,
    authenticate_user,
    get_user_by_email
)
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# New Pydantic models for OTP
class OTPRequest(BaseModel):
    email: str
    otp: str

class SendOTPRequest(BaseModel):
    email: str

# Global OTP storage (use Redis in production)
pending_otps: dict = {}

@router.post("/send-otp", response_model=dict)
async def send_otp(
    request: SendOTPRequest, 
    db: AsyncSession = Depends(get_db)
):
    """Send OTP to email (for registration verification)"""
    email = request.email.lower()
    
    # Check if user already exists and is active
    existing_user = await get_user_by_email(db, email)
    if existing_user and existing_user.is_active:
        raise HTTPException(409, "User already registered and active")
    
    # Generate 6-digit OTP
    otp = str(secrets.randbelow(1000000)).zfill(6)
    
    # Store OTP (expires in 10 minutes)
    pending_otps[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "user_data": None  # Will store user data after validation
    }
    
    # Send REAL email (production ready!)
    try:
        await send_real_email(email, otp)
        print(f"✅ REAL EMAIL sent to {email}: OTP {otp}")
    except Exception as e:
        print(f"❌ Email failed for {email}: {e}")
        # Don't fail the endpoint if email fails (fallback to console)
        print(f"🔐 FALLBACK - OTP for {email}: {otp}")
    
    return {
        "message": "OTP sent to your email (check inbox/spam)",
        "email": email,
        "expires_in_minutes": 10
    }

@router.post("/verify-otp", response_model=dict)
async def verify_otp(
    request: OTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify OTP and complete registration"""
    email = request.email.lower()
    
    # Check if OTP exists and is valid
    if email not in pending_otps:
        raise HTTPException(400, "No OTP found. Please request new OTP.")
    
    otp_data = pending_otps[email]
    if datetime.utcnow() > otp_data["expires_at"]:
        del pending_otps[email]
        raise HTTPException(400, "OTP expired. Request new OTP.")
    
    if otp_data["otp"] != request.otp:
        raise HTTPException(400, "Invalid OTP")
    
    # If user data exists, create user (from previous registration attempt)
    if otp_data["user_data"]:
        user_data = otp_data["user_data"]
        new_user = await create_user(db, user_data)
        del pending_otps[email]
        return {
            "message": "Registration completed successfully!",
            "user": UserResponse.from_orm(new_user)
        }
    
    return {"message": "OTP verified! Now complete your registration."}

@router.post("/register", response_model=dict)
async def register(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Step 1 of registration: Validate data → Send OTP"""
    email = user.email.lower()
    
    # Check if user already exists and active
    existing_user = await get_user_by_email(db, email)
    if existing_user and existing_user.is_active:
        raise HTTPException(409, "User already registered")
    
    # Store user data with OTP (for verification later)
    if email in pending_otps:
        pending_otps[email]["user_data"] = user.dict()
    
    # Send OTP
    return await send_otp(SendOTPRequest(email=email), db)

@router.post("/login", response_model=Token)
async def login(
    email: str, 
    password: str, 
    db: AsyncSession = Depends(get_db)
):
    """Normal login (after OTP verification)"""
    user = await authenticate_user(db, email, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account not verified. Complete OTP verification first.")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
