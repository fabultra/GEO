"""
Modèle Report - Rapports exportés
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Report(Base):
    """
    Table des rapports
    Rapports exportés (PDF, JSON, CSV, HTML)
    """
    __tablename__ = 'reports'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign keys
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Type et stockage
    report_type = Column(String(20), nullable=False)  # 'pdf', 'json', 'csv', 'html'
    file_path = Column(String(500))  # Chemin vers le fichier (ou S3 URL)
    file_size = Column(Integer)  # Taille en bytes

    # Timestamp
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    analysis = relationship('Analysis', back_populates='reports')
    user = relationship('User', back_populates='reports')

    def __repr__(self):
        return f"<Report(id={self.id}, type={self.report_type})>"
