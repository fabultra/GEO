"""
Modèle Website - Sites web analysés
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Website(Base):
    """
    Table des sites web
    Un utilisateur peut avoir plusieurs sites
    """
    __tablename__ = 'websites'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Informations du site
    url = Column(String(500), nullable=False)
    domain = Column(String(255), nullable=False, index=True)

    # Détection langue et localisation
    language_detected = Column(String(10))  # 'fr', 'en', 'fr-en'
    is_bilingual = Column(Boolean, default=False)
    is_quebec_brand = Column(Boolean, default=False)

    # Type de business (détecté par semantic analysis)
    business_type = Column(String(100))

    # Crawl info
    last_crawled_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship('User', back_populates='websites')
    analyses = relationship('Analysis', back_populates='website', cascade='all, delete-orphan')
    crawl_data = relationship('CrawlData', back_populates='website', cascade='all, delete-orphan')
    semantic_universe = relationship('SemanticUniverse', back_populates='website', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Website(id={self.id}, url={self.url})>"

    @property
    def latest_analysis(self):
        """Retourne la dernière analyse de ce site"""
        if self.analyses:
            return sorted(self.analyses, key=lambda a: a.created_at, reverse=True)[0]
        return None
