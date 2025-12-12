"""
Modèles SQLAlchemy pour GEO
Import centralisé de tous les modèles
"""
from database import Base

# Import all models
from .user import User
from .subscription import Subscription
from .website import Website
from .analysis import Analysis
from .crawl_data import CrawlData
from .semantic import SemanticUniverse
from .question import GeneratedQuestion
from .llm_test import LLMTestResult
from .competitor import Competitor, CompetitorAnalysis
from .recommendation import TechnicalRecommendation
from .content import OptimizedContent
from .learning import LearningData
from .report import Report
from .api_usage import APIUsageLog

__all__ = [
    'Base',
    'User',
    'Subscription',
    'Website',
    'Analysis',
    'CrawlData',
    'SemanticUniverse',
    'GeneratedQuestion',
    'LLMTestResult',
    'Competitor',
    'CompetitorAnalysis',
    'TechnicalRecommendation',
    'OptimizedContent',
    'LearningData',
    'Report',
    'APIUsageLog',
]
