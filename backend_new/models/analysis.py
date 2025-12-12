"""
Modèle Analysis - Analyses complètes GEO
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Analysis(Base):
    """
    Table des analyses
    Une analyse complète d'un site web
    """
    __tablename__ = 'analyses'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign keys
    website_id = Column(UUID(as_uuid=True), ForeignKey('websites.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Status et plan
    status = Column(String(20), default='pending', nullable=False)  # 'pending', 'crawling', 'analyzing', 'completed', 'failed'
    plan_type = Column(String(20), nullable=False)  # Plan utilisé pour cette analyse

    # Scores globaux (0-100)
    global_score = Column(Integer)

    # Scores détaillés par critère (0-100)
    score_structure = Column(Integer)
    score_machine_readability = Column(Integer)
    score_eeat = Column(Integer)
    score_educational_content = Column(Integer)
    score_thematic_organization = Column(Integer)
    score_ai_optimization = Column(Integer)
    score_semantic_richness = Column(Integer)
    score_domain_authority = Column(Integer)
    score_freshness = Column(Integer)
    score_user_intent = Column(Integer)

    # Métadonnées d'analyse
    pages_crawled = Column(Integer)
    total_questions_generated = Column(Integer)
    llm_tests_performed = Column(Integer)
    competitors_found = Column(Integer)

    # Erreurs
    error_message = Column(Text)

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship('User', back_populates='analyses')
    website = relationship('Website', back_populates='analyses')
    crawl_data = relationship('CrawlData', back_populates='analysis', cascade='all, delete-orphan')
    semantic_universe = relationship('SemanticUniverse', back_populates='analysis', cascade='all, delete-orphan')
    generated_questions = relationship('GeneratedQuestion', back_populates='analysis', cascade='all, delete-orphan')
    llm_test_results = relationship('LLMTestResult', back_populates='analysis', cascade='all, delete-orphan')
    competitors = relationship('Competitor', back_populates='analysis', cascade='all, delete-orphan')
    technical_recommendations = relationship('TechnicalRecommendation', back_populates='analysis', cascade='all, delete-orphan')
    optimized_content = relationship('OptimizedContent', back_populates='analysis', cascade='all, delete-orphan')
    reports = relationship('Report', back_populates='analysis', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Analysis(id={self.id}, status={self.status}, score={self.global_score})>"

    @property
    def is_completed(self) -> bool:
        """Vérifie si l'analyse est terminée"""
        return self.status == 'completed'

    @property
    def is_failed(self) -> bool:
        """Vérifie si l'analyse a échoué"""
        return self.status == 'failed'

    @property
    def duration_seconds(self) -> int:
        """Durée de l'analyse en secondes"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return 0

    def get_detailed_scores(self) -> dict:
        """Retourne tous les scores détaillés"""
        return {
            'global': self.global_score,
            'structure': self.score_structure,
            'machine_readability': self.score_machine_readability,
            'eeat': self.score_eeat,
            'educational_content': self.score_educational_content,
            'thematic_organization': self.score_thematic_organization,
            'ai_optimization': self.score_ai_optimization,
            'semantic_richness': self.score_semantic_richness,
            'domain_authority': self.score_domain_authority,
            'freshness': self.score_freshness,
            'user_intent': self.score_user_intent,
        }
