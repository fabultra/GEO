"""
Modèle LLMTestResult - Résultats des tests dans les LLMs
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class LLMTestResult(Base):
    """
    Table des résultats de tests LLM
    Résultat d'une question posée à un LLM spécifique
    """
    __tablename__ = 'llm_test_results'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign keys
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey('generated_questions.id', ondelete='CASCADE'), nullable=False, index=True)

    # LLM info
    llm_provider = Column(String(50), nullable=False)  # 'claude', 'chatgpt', 'perplexity', 'gemini'
    llm_model = Column(String(100))

    # Query et réponse
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)

    # Résultats de l'analyse
    brand_mentioned = Column(Boolean)
    brand_position = Column(Integer)  # Position dans la réponse (1-10, ou null)
    competitors_mentioned = Column(ARRAY(String))
    citations_count = Column(Integer)
    response_quality_score = Column(Integer)  # 0-100

    # Timestamp
    tested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    analysis = relationship('Analysis', back_populates='llm_test_results')
    question = relationship('GeneratedQuestion', back_populates='llm_test_results')

    def __repr__(self):
        return f"<LLMTestResult(id={self.id}, provider={self.llm_provider}, mentioned={self.brand_mentioned})>"
