from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
import re

class UserCreate(BaseModel):
    email: EmailStr = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    
    @field_validator('email')  # ← CHANGED: @validator → @field_validator
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError('Invalid email format')
        if v.lower().endswith('test') or v.lower().endswith('example'):
            raise ValueError('Test/example emails not allowed')
        return v.lower()
    
    @field_validator('password')  # ← CHANGED: @validator → @field_validator
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
    
    @field_validator('full_name')  # ← CHANGED: @validator → @field_validator
    @classmethod
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        if len(v.split()) < 2:  # First + Last name
            raise ValueError('Full name must include first and last name')
        if not v.replace(' ', '').replace('.', '').replace('-', '').isalpha():
            raise ValueError('Full name can only contain letters, spaces, dots, hyphens')
        return v.strip().title()

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
