"""
Schémas Pydantic pour Analysis
"""
from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional, List
from datetime import datetime


class AnalysisBase(BaseModel):
    """Base analysis schema"""
    pass


class AnalysisCreate(BaseModel):
    """Schema pour créer une analyse"""
    url: HttpUrl


class AnalysisScores(BaseModel):
    """Scores détaillés d'une analyse"""
    global_score: Optional[int] = None
    score_structure: Optional[int] = None
    score_machine_readability: Optional[int] = None
    score_eeat: Optional[int] = None
    score_educational_content: Optional[int] = None
    score_thematic_organization: Optional[int] = None
    score_ai_optimization: Optional[int] = None
    score_semantic_richness: Optional[int] = None
    score_domain_authority: Optional[int] = None
    score_freshness: Optional[int] = None
    score_user_intent: Optional[int] = None


class AnalysisStatusResponse(BaseModel):
    """Schema pour status d'analyse (polling)"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    progress: int = 0  # 0-100
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class AnalysisResponse(AnalysisStatusResponse):
    """Schema complet pour réponse analyse"""
    website_id: str
    user_id: str
    plan_type: str

    # Scores
    global_score: Optional[int] = None
    score_structure: Optional[int] = None
    score_machine_readability: Optional[int] = None
    score_eeat: Optional[int] = None
    score_educational_content: Optional[int] = None
    score_thematic_organization: Optional[int] = None
    score_ai_optimization: Optional[int] = None
    score_semantic_richness: Optional[int] = None
    score_domain_authority: Optional[int] = None
    score_freshness: Optional[int] = None
    score_user_intent: Optional[int] = None

    # Metadata
    pages_crawled: Optional[int] = None
    total_questions_generated: Optional[int] = None
    llm_tests_performed: Optional[int] = None
    competitors_found: Optional[int] = None

    created_at: datetime


class AnalysisListResponse(BaseModel):
    """Schema pour liste d'analyses"""
    analyses: List[AnalysisResponse]
    total: int
