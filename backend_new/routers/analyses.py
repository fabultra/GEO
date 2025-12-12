"""
Routes analyses
CRUD, status, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from urllib.parse import urlparse
import logging

from database import get_db
from models import User, Subscription, Website, Analysis
from schemas import (
    AnalysisCreate,
    AnalysisResponse,
    AnalysisListResponse,
    AnalysisStatusResponse,
)
from dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    analysis_data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Créer une nouvelle analyse

    - Vérifie les limites de la subscription
    - Crée ou récupère le website
    - Lance l'analyse en background
    """
    user_id = current_user["id"]

    # Récupérer la subscription
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Vérifier les limites
    if not subscription.can_create_analysis():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Monthly limit reached ({subscription.monthly_analyses_limit} analyses)"
        )

    # Extraire le domaine de l'URL
    url_str = str(analysis_data.url)
    parsed = urlparse(url_str)
    domain = parsed.netloc.replace('www.', '')

    # Créer ou récupérer le website
    website = db.query(Website).filter(
        Website.user_id == user_id,
        Website.url == url_str
    ).first()

    if not website:
        website = Website(
            user_id=user_id,
            url=url_str,
            domain=domain,
        )
        db.add(website)
        db.flush()

    # Créer l'analyse
    analysis = Analysis(
        website_id=website.id,
        user_id=user_id,
        status='pending',
        plan_type=subscription.plan_type,
    )

    db.add(analysis)

    # Incrémenter le compteur
    subscription.increment_usage()

    db.commit()
    db.refresh(analysis)

    logger.info(f"Analysis created: {analysis.id} for {url_str}")

    # TODO: Lancer l'analyse en background avec Celery
    # background_tasks.add_task(run_analysis_task, analysis.id)

    return analysis


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Lister les analyses de l'utilisateur connecté

    Pagination avec skip et limit
    """
    user_id = current_user["id"]

    # Compter le total
    total = db.query(Analysis).filter(Analysis.user_id == user_id).count()

    # Récupérer les analyses
    analyses = db.query(Analysis).filter(
        Analysis.user_id == user_id
    ).order_by(
        Analysis.created_at.desc()
    ).offset(skip).limit(limit).all()

    return AnalysisListResponse(
        analyses=analyses,
        total=total
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer une analyse spécifique

    - Vérifie que l'analyse appartient à l'utilisateur
    - Retourne toutes les informations
    """
    user_id = current_user["id"]

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    return analysis


@router.get("/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    analysis_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer juste le status d'une analyse (pour polling)

    Plus léger que get_analysis
    """
    user_id = current_user["id"]

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Calculer le progress (0-100)
    progress = 0
    if analysis.status == 'pending':
        progress = 0
    elif analysis.status == 'crawling':
        progress = 20
    elif analysis.status == 'analyzing':
        progress = 60
    elif analysis.status == 'completed':
        progress = 100
    elif analysis.status == 'failed':
        progress = 0

    return AnalysisStatusResponse(
        id=str(analysis.id),
        status=analysis.status,
        progress=progress,
        error_message=analysis.error_message,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at,
    )


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Supprimer une analyse

    - Vérifie que l'analyse appartient à l'utilisateur
    - Supprime l'analyse et toutes ses données (cascade)
    """
    user_id = current_user["id"]

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    db.delete(analysis)
    db.commit()

    logger.info(f"Analysis deleted: {analysis_id}")

    return None
