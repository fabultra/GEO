"""
Schémas Pydantic pour Website
"""
from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime


class WebsiteBase(BaseModel):
    """Base website schema"""
    url: HttpUrl


class WebsiteCreate(WebsiteBase):
    """Schema pour créer un website"""
    pass  # URL suffit, le reste est détecté automatiquement


class WebsiteResponse(WebsiteBase):
    """Schema pour réponse website"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    domain: str
    language_detected: Optional[str] = None
    is_bilingual: bool = False
    is_quebec_brand: bool = False
    business_type: Optional[str] = None
    last_crawled_at: Optional[datetime] = None
    created_at: datetime
