"""
Point d'entrée principal de l'application GEO
FastAPI application avec tous les routers
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from config import (
    API_PREFIX,
    CORS_ORIGINS,
    ENVIRONMENT,
    LOG_LEVEL,
    LOG_FORMAT,
)
from database import check_db_connection

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events pour FastAPI
    Startup et shutdown
    """
    # Startup
    logger.info(f"🚀 Starting GEO Application (Environment: {ENVIRONMENT})")

    # Vérifier connexion DB
    if check_db_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed")
        raise RuntimeError("Cannot connect to database")

    # TODO: Initialize Redis connection
    # TODO: Initialize Celery

    logger.info("✅ Application started successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down GEO Application")


# Create FastAPI app
app = FastAPI(
    title="GEO API",
    description="Generative Engine Optimization - API complète",
    version="2.0.0",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Ajoute le temps de traitement dans les headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global pour les exceptions non catchées"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if ENVIRONMENT == "development" else "An error occurred",
        }
    )


# Health check endpoint
@app.get(f"{API_PREFIX}/health")
async def health_check():
    """
    Health check endpoint
    Vérifie que l'API et la DB sont opérationnelles
    """
    db_status = check_db_connection()

    return {
        "status": "healthy" if db_status else "unhealthy",
        "environment": ENVIRONMENT,
        "database": "connected" if db_status else "disconnected",
        # TODO: Add Redis status
        # TODO: Add Celery status
    }


# Root endpoint
@app.get(f"{API_PREFIX}/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "GEO API",
        "version": "2.0.0",
        "description": "Generative Engine Optimization API",
        "environment": ENVIRONMENT,
        "docs": f"{API_PREFIX}/docs",
    }


# Import et inclure les routers
from routers import (
    auth_router,
    users_router,
    analyses_router,
    reports_router,
    admin_router,
)

app.include_router(auth_router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(users_router, prefix=f"{API_PREFIX}/users", tags=["Users"])
app.include_router(analyses_router, prefix=f"{API_PREFIX}/analyses", tags=["Analyses"])
app.include_router(reports_router, prefix=f"{API_PREFIX}/reports", tags=["Reports"])
app.include_router(admin_router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=ENVIRONMENT == "development",
        log_level=LOG_LEVEL.lower(),
    )
