"""
Modèle Subscription - Abonnements et forfaits
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database import Base
from config import get_plan_features


class Subscription(Base):
    """
    Table des abonnements
    Gère les forfaits FREE/PRO/BUSINESS et les limites
    """
    __tablename__ = 'subscriptions'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Plan details
    plan_type = Column(String(20), nullable=False)  # 'free', 'pro', 'business'
    status = Column(String(20), default='active', nullable=False)  # 'active', 'cancelled', 'expired'

    # Limites
    monthly_analyses_limit = Column(Integer, nullable=False)
    analyses_used = Column(Integer, default=0, nullable=False)

    # Prix
    price_monthly = Column(Numeric(10, 2))

    # Dates
    start_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship('User', back_populates='subscription')

    def __repr__(self):
        return f"<Subscription(id={self.id}, plan={self.plan_type}, status={self.status})>"

    def can_create_analysis(self) -> bool:
        """Vérifie si l'utilisateur peut créer une nouvelle analyse"""
        if self.status != 'active':
            return False

        if self.end_date and self.end_date < datetime.now():
            return False

        return self.analyses_used < self.monthly_analyses_limit

    def increment_usage(self):
        """Incrémente le compteur d'analyses utilisées"""
        self.analyses_used += 1

    def reset_monthly_usage(self):
        """Réinitialise le compteur mensuel (cron job)"""
        self.analyses_used = 0

    def get_features(self) -> dict:
        """Retourne les features disponibles pour ce plan"""
        return get_plan_features(self.plan_type)

    def can_use_feature(self, feature: str) -> bool:
        """Vérifie si une feature est disponible"""
        features = self.get_features()
        return feature in features.get('features', [])

    @property
    def analyses_remaining(self) -> int:
        """Nombre d'analyses restantes ce mois"""
        return max(0, self.monthly_analyses_limit - self.analyses_used)
