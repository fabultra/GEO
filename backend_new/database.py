"""
Configuration SQLAlchemy et gestion de la connexion PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifie connexion avant utilisation
    pool_size=10,  # Pool de connexions
    max_overflow=20,  # Connexions additionnelles
    echo=False,  # Logs SQL (True en dev si besoin)
)

# SessionLocal factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection pour obtenir une session DB
    Usage dans FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialise la base de données
    Crée toutes les tables si elles n'existent pas
    À utiliser UNIQUEMENT en développement
    En production, utiliser Alembic migrations
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def check_db_connection() -> bool:
    """
    Vérifie que la connexion à la DB fonctionne
    Utile pour health checks
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
