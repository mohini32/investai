"""
Authentication schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from app.schemas.user import UserResponse


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str
    full_name: str
    password: str
    phone_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only letters and numbers')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token data"""
    user_id: Optional[int] = None


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
