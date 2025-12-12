"""
Modèle SemanticUniverse - Univers sémantique du site
"""
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class SemanticUniverse(Base):
    """
    Table de l'univers sémantique
    Résultat de l'analyse sémantique profonde
    """
    __tablename__ = 'semantic_universe'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign keys
    website_id = Column(UUID(as_uuid=True), ForeignKey('websites.id', ondelete='CASCADE'), nullable=False, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)

    # Keywords et topics (JSON)
    keywords = Column(JSONB)  # {keyword: frequency}
    topics = Column(JSONB)  # [topic1, topic2, ...]
    entities = Column(JSONB)  # {entity: count}

    # Thèmes identifiés
    themes = Column(ARRAY(String))

    # Type de business détecté
    business_type_detected = Column(String(100))

    # Clusters sémantiques
    semantic_clusters = Column(JSONB)

    # Timestamp
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    website = relationship('Website', back_populates='semantic_universe')
    analysis = relationship('Analysis', back_populates='semantic_universe')

    def __repr__(self):
        return f"<SemanticUniverse(id={self.id}, business_type={self.business_type_detected})>"
