"""
Routes admin (super_admin seulement)
Gestion users, subscriptions, stats
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from models import User, Subscription, Analysis
from schemas import (
    UserResponse,
    UserWithSubscription,
    SubscriptionUpdate,
    AnalysisResponse,
)
from dependencies import require_role

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users", response_model=List[UserWithSubscription])
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_role('super_admin')),
    db: Session = Depends(get_db)
):
    """
    Lister tous les utilisateurs (admin seulement)

    Inclut leurs subscriptions
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/analyses", response_model=List[AnalysisResponse])
async def list_all_analyses(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_role('super_admin')),
    db: Session = Depends(get_db)
):
    """
    Lister toutes les analyses (admin seulement)

    Tous les utilisateurs confondus
    """
    analyses = db.query(Analysis).order_by(
        Analysis.created_at.desc()
    ).offset(skip).limit(limit).all()

    return analyses


@router.put("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: str,
    subscription_data: SubscriptionUpdate,
    current_user: dict = Depends(require_role('super_admin')),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour la subscription d'un utilisateur (admin seulement)

    Peut modifier:
    - plan_type
    - status
    - monthly_analyses_limit
    - analyses_used (reset)
    - end_date
    """
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Mettre à jour les champs fournis
    if subscription_data.plan_type is not None:
        subscription.plan_type = subscription_data.plan_type
    if subscription_data.status is not None:
        subscription.status = subscription_data.status
    if subscription_data.monthly_analyses_limit is not None:
        subscription.monthly_analyses_limit = subscription_data.monthly_analyses_limit
    if subscription_data.analyses_used is not None:
        subscription.analyses_used = subscription_data.analyses_used
    if subscription_data.end_date is not None:
        subscription.end_date = subscription_data.end_date

    db.commit()
    db.refresh(subscription)

    logger.info(f"Subscription updated by admin: {user_id}")

    return subscription


@router.get("/stats")
async def get_global_stats(
    current_user: dict = Depends(require_role('super_admin')),
    db: Session = Depends(get_db)
):
    """
    Récupérer les statistiques globales (admin seulement)

    - Nombre total d'utilisateurs
    - Nombre total d'analyses
    - Répartition par forfait
    - etc.
    """
    total_users = db.query(User).count()
    total_analyses = db.query(Analysis).count()

    # Analyses par statut
    analyses_by_status = {}
    for status in ['pending', 'crawling', 'analyzing', 'completed', 'failed']:
        count = db.query(Analysis).filter(Analysis.status == status).count()
        analyses_by_status[status] = count

    # Subscriptions par plan
    subscriptions_by_plan = {}
    for plan in ['free', 'pro', 'business']:
        count = db.query(Subscription).filter(Subscription.plan_type == plan).count()
        subscriptions_by_plan[plan] = count

    return {
        "total_users": total_users,
        "total_analyses": total_analyses,
        "analyses_by_status": analyses_by_status,
        "subscriptions_by_plan": subscriptions_by_plan,
    }
