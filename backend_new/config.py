"""
Configuration centralisée pour GEO - Architecture Production
Toutes les variables d'environnement et constantes
"""
import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

# Chemins
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent

# Base de données PostgreSQL
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://localhost/geo_production'
)

# Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Clés API
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# JWT Authentication
JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-in-production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_MINUTES = int(os.getenv('JWT_EXPIRATION_MINUTES', '60'))
JWT_REFRESH_EXPIRATION_DAYS = int(os.getenv('JWT_REFRESH_EXPIRATION_DAYS', '30'))

# Application
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = ENVIRONMENT == 'development'
API_PREFIX = '/api'
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# CORS
CORS_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'https://geo.sekoia.ca',
]

# Modèles IA
CLAUDE_MODEL = 'claude-sonnet-4-20250514'
CLAUDE_MAX_TOKENS = 8192
CLAUDE_TEMPERATURE = 0  # Déterministe pour GEO

GPT_MODEL = 'gpt-4-turbo-preview'
GPT_MAX_TOKENS = 4096
GPT_TEMPERATURE = 0

# Crawling
MAX_PAGES_TO_CRAWL = 200  # Adaptatif selon taille site
CRAWL_DELAY_SECONDS = 1.0
CRAWL_TIMEOUT_SECONDS = 15
USER_AGENT = 'Mozilla/5.0 (compatible; GEOBot/2.0; +https://geo.sekoia.ca/bot)'

# Analyse sémantique
MAX_PAGES_TO_ANALYZE = 50
SEMANTIC_ANALYSIS_TIMEOUT = 60  # secondes

# Génération de requêtes
QUERIES_TOTAL = 100
QUERIES_NON_BRANDED_PERCENT = 80
QUERIES_SEMI_BRANDED_PERCENT = 15
QUERIES_BRANDED_PERCENT = 5

# Tests de visibilité
VISIBILITY_PLATFORMS = ['chatgpt', 'claude', 'perplexity', 'gemini']
VISIBILITY_TIMEOUT_SECONDS = 30
VISIBILITY_MAX_RETRIES = 3
VISIBILITY_RETRY_DELAY = 2  # secondes

# Découverte de compétiteurs
MAX_COMPETITORS = 5
COMPETITOR_SEARCH_TIMEOUT = 15
COMPETITOR_VALIDATION_TIMEOUT = 10
COMPETITOR_MAX_RETRIES = 2
COMPETITOR_RELEVANCE_THRESHOLD_DIRECT = 0.6
COMPETITOR_RELEVANCE_THRESHOLD_INDIRECT = 0.3
# Utiliser SerpAPI pour recherches Google (plus stable que scraping)
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
USE_SERPAPI = bool(SERPAPI_API_KEY)

# Cache Redis
CACHE_ENABLED = True
CACHE_TTL_ANALYSIS = 604800  # 7 jours
CACHE_TTL_COMPETITORS = 2592000  # 30 jours
CACHE_TTL_VISIBILITY = 604800  # 7 jours

# Rate Limiting
RATE_LIMIT_ANTHROPIC = 10  # requêtes par minute
RATE_LIMIT_OPENAI = 20
RATE_LIMIT_PERPLEXITY = 5

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 1800  # 30 minutes max par task

# Subscriptions & Pricing
SUBSCRIPTION_PLANS = {
    'free': {
        'monthly_analyses_limit': 1,
        'price_monthly': 0.0,
        'features': [
            'score_global',
            'basic_recommendations',
        ],
        'disabled_features': [
            'competitive_analysis',
            'technical_code',
            'optimized_content',
        ]
    },
    'pro': {
        'monthly_analyses_limit': 5,
        'price_monthly': 1500.0,  # CAD
        'features': [
            'score_global',
            'detailed_scores',
            'competitive_analysis',
            'technical_code',
            'gap_analysis',
            'advanced_recommendations',
            'llm_tests',
        ],
        'max_competitors': 5,
    },
    'business': {
        'monthly_analyses_limit': 20,
        'price_monthly': 5000.0,  # CAD
        'features': [
            'score_global',
            'detailed_scores',
            'competitive_analysis',
            'technical_code',
            'gap_analysis',
            'advanced_recommendations',
            'llm_tests',
            'optimized_content',
            'api_access',
            'white_label_reports',
            'priority_support',
        ],
        'max_competitors': 10,
    }
}

# Rapports
REPORT_FORMATS = ['json', 'pdf', 'csv', 'html']
REPORT_RETENTION_DAYS = 90

# Logs
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# API Usage Tracking
TRACK_API_COSTS = True
ANTHROPIC_COST_PER_1M_INPUT = 3.0  # USD
ANTHROPIC_COST_PER_1M_OUTPUT = 15.0  # USD
OPENAI_COST_PER_1M_INPUT = 10.0  # USD
OPENAI_COST_PER_1M_OUTPUT = 30.0  # USD


@lru_cache()
def get_settings():
    """
    Retourne les settings (cached)
    Utile pour dependency injection FastAPI
    """
    return {
        'database_url': DATABASE_URL,
        'redis_url': REDIS_URL,
        'environment': ENVIRONMENT,
        'debug': DEBUG,
        'api_prefix': API_PREFIX,
        'frontend_url': FRONTEND_URL,
    }


def is_production() -> bool:
    """Vérifie si on est en production"""
    return ENVIRONMENT.lower() == 'production'


def is_development() -> bool:
    """Vérifie si on est en développement"""
    return ENVIRONMENT.lower() == 'development'


def get_plan_features(plan_type: str) -> dict:
    """Retourne les features d'un plan"""
    return SUBSCRIPTION_PLANS.get(plan_type, SUBSCRIPTION_PLANS['free'])


def can_use_feature(plan_type: str, feature: str) -> bool:
    """Vérifie si un plan a accès à une feature"""
    plan = get_plan_features(plan_type)
    return feature in plan.get('features', [])
