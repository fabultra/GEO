"""
Schémas Pydantic - Import centralisé
"""
from .user import UserCreate, UserLogin, UserResponse, UserUpdate, TokenResponse
from .subscription import SubscriptionResponse, SubscriptionUpdate
from .website import WebsiteCreate, WebsiteResponse
from .analysis import AnalysisCreate, AnalysisResponse, AnalysisStatusResponse, AnalysisScores
from .report import ReportExport, ReportResponse

__all__ = [
    # User & Auth
    'UserCreate',
    'UserLogin',
    'UserResponse',
    'UserUpdate',
    'TokenResponse',
    # Subscription
    'SubscriptionResponse',
    'SubscriptionUpdate',
    # Website
    'WebsiteCreate',
    'WebsiteResponse',
    # Analysis
    'AnalysisCreate',
    'AnalysisResponse',
    'AnalysisStatusResponse',
    'AnalysisScores',
    # Report
    'ReportExport',
    'ReportResponse',
]
