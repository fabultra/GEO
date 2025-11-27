"""
Configuration centralisée pour l'application GEO
Toutes les constantes et paramètres configurables
"""
import os
from pathlib import Path
from typing import Optional

# Chemins
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR.parent / "data"
CACHE_DIR = ROOT_DIR / "cache"
REPORTS_DIR = ROOT_DIR / "reports"
DASHBOARDS_DIR = ROOT_DIR / "dashboards"

# Créer les dossiers s'ils n'existent pas
CACHE_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
DASHBOARDS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Base de données
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'geo_saas')

# Clés API
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Modèles IA
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_MAX_TOKENS = 8192
CLAUDE_TEMPERATURE = 0  # Déterministe

# Crawling
MAX_PAGES_TO_CRAWL = 10
CRAWL_DELAY_SECONDS = 0.5
CRAWL_TIMEOUT_SECONDS = 10
USER_AGENT = 'Mozilla/5.0 (compatible; GEOBot/1.0)'

# Analyse
MAX_PAGES_TO_ANALYZE = 8  # Pages envoyées à Claude
ANALYSIS_RETRY_COUNT = 3
ANALYSIS_RETRY_DELAY_BASE = 2  # Secondes (backoff exponentiel)

# Génération de requêtes
QUERIES_TOTAL_TARGET = 100
QUERIES_NON_BRANDED_PERCENT = 80
QUERIES_SEMI_BRANDED_PERCENT = 15
QUERIES_BRANDED_PERCENT = 5

# Tests de visibilité
VISIBILITY_PLATFORMS = ['chatgpt', 'claude', 'perplexity', 'gemini', 'google_ai']
VISIBILITY_TIMEOUT_SECONDS = 30
VISIBILITY_MAX_QUERIES = 100

# Cache
CACHE_ENABLED = True
CACHE_TTL_HOURS = 168  # 7 jours
CACHE_ANALYSIS_ENABLED = True
CACHE_VISIBILITY_ENABLED = True

# Nettoyage automatique
CLEANUP_TEMP_FILES_DAYS = 7
CLEANUP_REPORTS_DAYS = 30
CLEANUP_CACHE_DAYS = 7

# Rapports
WORD_REPORT_MIN_PAGES = 50
WORD_REPORT_MAX_PAGES = 70
RECOMMENDATIONS_COUNT = 20
QUICK_WINS_COUNT = 8

# Serveur
API_PREFIX = "/api"
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

# CORS
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8001",
    "https://*.emergentagent.com",
]

# Limites de taux (pour éviter les abus)
RATE_LIMIT_ANALYSES_PER_HOUR = 10
RATE_LIMIT_REPORTS_PER_DAY = 50

# Découverte de compétiteurs
MAX_COMPETITORS = 5
COMPETITOR_SEARCH_PROVIDER = os.environ.get('GEO_SEARCH_PROVIDER', 'google_scrape')
SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')  # Optionnel
COMPETITOR_SEARCH_TIMEOUT = 10  # secondes
COMPETITOR_SEARCH_DELAY = 2  # secondes entre requêtes
COMPETITOR_VALIDATION_TIMEOUT = 5  # secondes pour HEAD request
COMPETITOR_MAX_RETRIES = 2
COMPETITOR_RELEVANCE_THRESHOLD_DIRECT = 0.6  # Score min pour "direct"
COMPETITOR_RELEVANCE_THRESHOLD_INDIRECT = 0.3  # Score min pour "indirect"


def get_api_key(service: str) -> Optional[str]:
    """
    Récupère la clé API appropriée pour un service
    Priorité : Clé spécifique > EMERGENT_LLM_KEY
    """
    if service == 'anthropic':
        return ANTHROPIC_API_KEY or EMERGENT_LLM_KEY
    elif service == 'openai':
        return OPENAI_API_KEY or EMERGENT_LLM_KEY
    return None


def is_production() -> bool:
    """Vérifie si on est en environnement de production"""
    return ENVIRONMENT.lower() == 'production'


def is_cache_enabled() -> bool:
    """Vérifie si le cache est activé"""
    return CACHE_ENABLED and not is_production()  # Désactiver en prod pour tests
