"""
Modèle OptimizedContent - Contenu optimisé généré (forfait BUSINESS)
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class OptimizedContent(Base):
    """
    Table du contenu optimisé
    Contenu généré par IA pour chaque page (forfait BUSINESS)
    """
    __tablename__ = 'optimized_content'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign key
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)

    # Page ciblée
    page_url = Column(String(500))
    page_level = Column(Integer)

    # Contenu optimisé
    optimized_title = Column(String(255))
    optimized_meta_description = Column(Text)
    optimized_h1 = Column(Text)
    optimized_content = Column(Text)

    # FAQ optimisée (JSON)
    optimized_faq = Column(JSONB)  # [{question, answer}, ...]

    # Suggestions de liens internes
    internal_links_suggestions = Column(ARRAY(Text))

    # Keywords ciblés
    keywords_targeted = Column(ARRAY(Text))

    # Statistiques
    word_count = Column(Integer)

    # Timestamp
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    analysis = relationship('Analysis', back_populates='optimized_content')

    def __repr__(self):
        return f"<OptimizedContent(id={self.id}, page_url={self.page_url})>"
