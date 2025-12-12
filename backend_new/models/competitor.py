"""
Modèles Competitor et CompetitorAnalysis
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Competitor(Base):
    """
    Table des compétiteurs découverts
    Stocke les compétiteurs identifiés pendant l'analyse
    """
    __tablename__ = 'competitors'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign keys
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)
    website_id = Column(UUID(as_uuid=True), ForeignKey('websites.id', ondelete='CASCADE'), nullable=False, index=True)

    # Informations compétiteur
    competitor_domain = Column(String(255), nullable=False)
    competitor_url = Column(String(500))

    # Méthode de découverte
    discovery_method = Column(String(50))  # 'semantic_search', 'llm_mention', 'manual', 'web_search'

    # Statistiques
    mention_count = Column(Integer, default=1)
    avg_position = Column(Numeric(5, 2))  # Position moyenne dans les réponses LLM
    relevance_score = Column(Integer)  # Score de pertinence 0-100

    # Timestamp
    discovered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    analysis = relationship('Analysis', back_populates='competitors')
    website = relationship('Website')
    competitor_analysis = relationship('CompetitorAnalysis', back_populates='competitor', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Competitor(id={self.id}, domain={self.competitor_domain}, method={self.discovery_method})>"


class CompetitorAnalysis(Base):
    """
    Table des analyses de compétiteurs
    Analyse complète d'un compétiteur (scores, forces, faiblesses)
    """
    __tablename__ = 'competitor_analyses'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign keys
    competitor_id = Column(UUID(as_uuid=True), ForeignKey('competitors.id', ondelete='CASCADE'), unique=True, nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)

    # Scores du compétiteur (même structure que Analysis)
    global_score = Column(Integer)
    score_structure = Column(Integer)
    score_machine_readability = Column(Integer)
    score_eeat = Column(Integer)
    score_educational_content = Column(Integer)
    score_thematic_organization = Column(Integer)
    score_ai_optimization = Column(Integer)

    # Gap analysis
    gap_global = Column(Integer)  # Différence de score global
    strengths = Column(ARRAY(Text))  # Forces du compétiteur
    weaknesses = Column(ARRAY(Text))  # Faiblesses du compétiteur
    opportunities = Column(ARRAY(Text))  # Opportunités pour nous

    # Timestamp
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    competitor = relationship('Competitor', back_populates='competitor_analysis')
    analysis = relationship('Analysis')

    def __repr__(self):
        return f"<CompetitorAnalysis(id={self.id}, score={self.global_score}, gap={self.gap_global})>"
