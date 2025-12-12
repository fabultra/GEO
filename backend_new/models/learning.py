"""
Modèle LearningData - Données d'apprentissage continu
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from database import Base


class LearningData(Base):
    """
    Table des données d'apprentissage
    Stocke les patterns de succès pour améliorer l'outil au fil du temps
    """
    __tablename__ = 'learning_data'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Classification
    industry = Column(String(100), index=True)
    business_type = Column(String(100))
    pattern_type = Column(String(50))  # 'successful_question', 'effective_optimization', 'high_scoring_structure'

    # Données du pattern (JSON flexible)
    pattern_data = Column(JSONB)

    # Statistiques
    success_rate = Column(Numeric(5, 2))  # 0.00 - 100.00
    usage_count = Column(Integer, default=1)

    # Timestamps
    last_used = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<LearningData(id={self.id}, industry={self.industry}, type={self.pattern_type})>"
