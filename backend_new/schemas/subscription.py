"""
Schémas Pydantic pour Subscription
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SubscriptionBase(BaseModel):
    """Base subscription schema"""
    plan_type: str = Field(..., pattern="^(free|pro|business)$")


class SubscriptionResponse(SubscriptionBase):
    """Schema pour réponse subscription"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    status: str
    monthly_analyses_limit: int
    analyses_used: int
    price_monthly: Optional[Decimal] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime

    # Computed fields
    @property
    def analyses_remaining(self) -> int:
        return max(0, self.monthly_analyses_limit - self.analyses_used)


class SubscriptionUpdate(BaseModel):
    """Schema pour mettre à jour une subscription (admin only)"""
    plan_type: Optional[str] = Field(None, pattern="^(free|pro|business)$")
    status: Optional[str] = Field(None, pattern="^(active|cancelled|expired)$")
    monthly_analyses_limit: Optional[int] = Field(None, ge=0)
    analyses_used: Optional[int] = Field(None, ge=0)
    end_date: Optional[datetime] = None


class SubscriptionCreate(SubscriptionBase):
    """Schema pour créer une subscription"""
    user_id: str
    monthly_analyses_limit: int
    price_monthly: Optional[Decimal] = None
