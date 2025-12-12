"""
Routes utilisateurs
Profil, subscription, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import User, Subscription
from schemas import UserResponse, UserUpdate, UserWithSubscription, SubscriptionResponse
from dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=UserWithSubscription)
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer les informations de l'utilisateur connecté

    Inclut sa subscription
    """
    user_id = current_user["id"]
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour les informations de l'utilisateur connecté

    - Peut mettre à jour: first_name, last_name, email
    - Ne peut PAS mettre à jour: password (route séparée), role
    """
    user_id = current_user["id"]
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Vérifier si le nouvel email existe déjà
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

    # Mettre à jour les champs fournis
    if user_data.first_name is not None:
        user.first_name = user_data.first_name
    if user_data.last_name is not None:
        user.last_name = user_data.last_name
    if user_data.email is not None:
        user.email = user_data.email

    db.commit()
    db.refresh(user)

    logger.info(f"User updated: {user.email}")

    return user


@router.get("/me/subscription", response_model=SubscriptionResponse)
async def get_current_user_subscription(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer la subscription de l'utilisateur connecté
    """
    user_id = current_user["id"]
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    return subscription
