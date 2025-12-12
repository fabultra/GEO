"""
Modèle TechnicalRecommendation - Recommandations techniques avec code généré
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class TechnicalRecommendation(Base):
    """
    Table des recommandations techniques
    Code généré (schema.org, meta tags, etc.)
    """
    __tablename__ = 'technical_recommendations'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign key
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)

    # Type de recommandation
    recommendation_type = Column(String(50), nullable=False)  # 'schema_org', 'meta_tags', 'structured_data', 'headers', 'internal_linking', 'faq'

    # Page ciblée
    page_url = Column(String(500))

    # Priorité
    priority = Column(String(20))  # 'critical', 'high', 'medium', 'low'

    # Code et instructions
    code_snippet = Column(Text)
    implementation_notes = Column(Text)

    # Impact estimé
    estimated_impact = Column(Integer)  # 0-100

    # Timestamp
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    analysis = relationship('Analysis', back_populates='technical_recommendations')

    def __repr__(self):
        return f"<TechnicalRecommendation(id={self.id}, type={self.recommendation_type}, priority={self.priority})>"
