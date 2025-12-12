"""
Routers FastAPI
"""
from .auth import router as auth_router
from .users import router as users_router
from .analyses import router as analyses_router
from .reports import router as reports_router
from .admin import router as admin_router

__all__ = [
    'auth_router',
    'users_router',
    'analyses_router',
    'reports_router',
    'admin_router',
]
