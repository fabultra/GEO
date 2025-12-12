"""
Modèle GeneratedQuestion - Questions générées pour tests LLM
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class GeneratedQuestion(Base):
    """
    Table des questions générées
    Questions utilisées pour tester la visibilité dans les LLMs
    """
    __tablename__ = 'generated_questions'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign key
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)

    # Question
    question = Column(Text, nullable=False)
    question_type = Column(String(50))  # 'informational', 'transactional', 'navigational', etc.
    language = Column(String(10))  # 'fr', 'en'

    # Score de pertinence (0-100)
    relevance_score = Column(Integer)

    # Timestamp
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    analysis = relationship('Analysis', back_populates='generated_questions')
    llm_test_results = relationship('LLMTestResult', back_populates='question', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<GeneratedQuestion(id={self.id}, type={self.question_type})>"
