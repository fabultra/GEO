"""
Modèle User - Utilisateurs de l'application
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from database import Base


class User(Base):
    """
    Table des utilisateurs
    Gère l'authentification et l'autorisation
    """
    __tablename__ = 'users'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identification
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Informations personnelles
    first_name = Column(String(100))
    last_name = Column(String(100))

    # Rôle et statut
    role = Column(String(20), nullable=False, default='client')  # 'super_admin', 'client'
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    subscription = relationship('Subscription', back_populates='user', uselist=False)
    websites = relationship('Website', back_populates='user', cascade='all, delete-orphan')
    analyses = relationship('Analysis', back_populates='user', cascade='all, delete-orphan')
    reports = relationship('Report', back_populates='user', cascade='all, delete-orphan')
    api_usage_logs = relationship('APIUsageLog', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def full_name(self):
        """Retourne le nom complet"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def is_super_admin(self):
        """Vérifie si l'utilisateur est super admin"""
        return self.role == 'super_admin'

    def can_create_analysis(self):
        """Vérifie si l'utilisateur peut créer une analyse"""
        if not self.subscription:
            return False
        return self.subscription.can_create_analysis()
