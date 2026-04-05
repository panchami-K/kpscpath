import secrets
import aiosmtplib
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.user import Otp  # You'll need this model

async def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return str(secrets.randbelow(1000000)).zfill(6)

async def send_email_otp(email: str, otp: str):
    """Send OTP via SMTP"""
    msg = f"""
    <h2>KPSCPath Verification</h2>
    <p>Your OTP is: <strong style='font-size: 24px; color: #007bff'>{otp}</strong></p>
    <p>Valid for 10 minutes.</p>
    """
    
    await aiosmtplib.send(
        msg,
        sender=settings.SMTP_USER,
        recipients=[email],
        host=settings.SMTP_HOST,
        port=int(settings.SMTP_PORT),
        user=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        use_tls=True
    )

async def create_otp_record(db: AsyncSession, email: str, otp: str):
    """Store OTP in database (expires in 10min)"""
    otp_record = Otp(
        email=email,
        otp=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        is_used=False
    )
    db.add(otp_record)
    await db.commit()
