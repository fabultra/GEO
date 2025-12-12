"""
Modèle APIUsageLog - Tracking des coûts API
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class APIUsageLog(Base):
    """
    Table des logs d'usage API
    Tracking précis des coûts pour chaque appel API
    """
    __tablename__ = 'api_usage_logs'

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: __import__('uuid').uuid4())

    # Foreign keys (optionnels pour certains calls)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analyses.id'), index=True)

    # API info
    api_provider = Column(String(50), nullable=False)  # 'anthropic', 'openai', 'perplexity'
    endpoint = Column(String(100))

    # Tokens et coûts
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    cost_usd = Column(Numeric(10, 6))  # Coût en USD (précision 6 décimales)

    # Performance
    response_time_ms = Column(Integer)  # Temps de réponse en millisecondes

    # Timestamp
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='api_usage_logs')
    analysis = relationship('Analysis')

    def __repr__(self):
        return f"<APIUsageLog(id={self.id}, provider={self.api_provider}, cost=${self.cost_usd})>"

    @staticmethod
    def calculate_cost(provider: str, tokens_input: int, tokens_output: int) -> float:
        """
        Calcule le coût en USD pour un appel API
        """
        from config import ANTHROPIC_COST_PER_1M_INPUT, ANTHROPIC_COST_PER_1M_OUTPUT
        from config import OPENAI_COST_PER_1M_INPUT, OPENAI_COST_PER_1M_OUTPUT

        if provider == 'anthropic':
            cost = (
                (tokens_input / 1_000_000) * ANTHROPIC_COST_PER_1M_INPUT +
                (tokens_output / 1_000_000) * ANTHROPIC_COST_PER_1M_OUTPUT
            )
        elif provider == 'openai':
            cost = (
                (tokens_input / 1_000_000) * OPENAI_COST_PER_1M_INPUT +
                (tokens_output / 1_000_000) * OPENAI_COST_PER_1M_OUTPUT
            )
        else:
            cost = 0.0

        return round(cost, 6)
