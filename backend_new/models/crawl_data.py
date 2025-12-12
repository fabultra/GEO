"""
Modèle CrawlData - Données du crawl
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class CrawlData(Base):
    """
    Table des données de crawl
    Stocke chaque page crawlée avec son contenu
    """
    __tablename__ = 'crawl_data'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign keys
    website_id = Column(UUID(as_uuid=True), ForeignKey('websites.id', ondelete='CASCADE'), nullable=False, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)

    # URL et niveau
    url = Column(String(500), nullable=False)
    page_level = Column(Integer)  # 1, 2, 3 (profondeur dans le site)

    # Métadonnées
    title = Column(Text)
    meta_description = Column(Text)

    # Headings (stockés comme array)
    h1 = Column(ARRAY(Text))
    h2 = Column(ARRAY(Text))
    h3 = Column(ARRAY(Text))

    # Contenu
    content_text = Column(Text)
    content_length = Column(Integer)

    # Schema.org et structured data
    has_schema_org = Column(Boolean, default=False)
    schema_types = Column(ARRAY(String))

    # Liens
    internal_links = Column(Integer)
    external_links = Column(Integer)

    # Images
    images_count = Column(Integer)

    # Langue
    language = Column(String(10))

    # Timestamp
    crawled_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    website = relationship('Website', back_populates='crawl_data')
    analysis = relationship('Analysis', back_populates='crawl_data')

    def __repr__(self):
        return f"<CrawlData(id={self.id}, url={self.url}, level={self.page_level})>"
