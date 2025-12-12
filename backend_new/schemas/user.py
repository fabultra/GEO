"""
Schémas Pydantic pour User et Authentication
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr


class UserCreate(UserBase):
    """Schema pour créer un utilisateur"""
    password: str = Field(..., min_length=8, description="Minimum 8 caractères")
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema pour login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema pour mettre à jour un utilisateur"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema pour réponse user (sans password)"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class UserWithSubscription(UserResponse):
    """User avec sa subscription"""
    from .subscription import SubscriptionResponse

    subscription: Optional[SubscriptionResponse] = None


class TokenResponse(BaseModel):
    """Schema pour réponse JWT tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema pour refresh token"""
    refresh_token: str
