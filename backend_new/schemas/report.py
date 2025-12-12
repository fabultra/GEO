"""
Schémas Pydantic pour Report
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ReportExport(BaseModel):
    """Schema pour export de rapport"""
    format: str = Field(..., pattern="^(pdf|json|csv|html)$")


class ReportResponse(BaseModel):
    """Schema pour réponse report"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    user_id: str
    report_type: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generated_at: datetime
