"""
Routes d'authentification
Login, Register, Refresh, Logout
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import uuid

from database import get_db
from models import User, Subscription
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from config import SUBSCRIPTION_PLANS

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Créer un nouveau compte utilisateur

    - Vérifie que l'email n'existe pas déjà
    - Crée l'utilisateur avec password hashé
    - Crée une subscription FREE automatiquement
    - Retourne les JWT tokens
    """
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Créer l'utilisateur
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_pw,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role='client',  # Par défaut
        is_active=True,
    )

    db.add(new_user)
    db.flush()  # Pour obtenir l'ID

    # Créer subscription FREE automatiquement
    free_plan = SUBSCRIPTION_PLANS['free']
    subscription = Subscription(
        user_id=new_user.id,
        plan_type='free',
        status='active',
        monthly_analyses_limit=free_plan['monthly_analyses_limit'],
        analyses_used=0,
        price_monthly=free_plan['price_monthly'],
    )

    db.add(subscription)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")

    # Créer les tokens
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Se connecter avec email et password

    - Vérifie les credentials
    - Vérifie que l'utilisateur est actif
    - Retourne les JWT tokens
    """
    # Chercher l'utilisateur
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    logger.info(f"User logged in: {user.email}")

    # Créer les tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Rafraîchir l'access token avec un refresh token

    - Vérifie que le refresh token est valide
    - Crée un nouvel access token
    - Retourne les nouveaux tokens
    """
    # Vérifier le refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    # Récupérer l'utilisateur
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Créer nouveaux tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    """
    Se déconnecter

    Note: Avec JWT stateless, le logout côté serveur est minimal.
    Le client doit supprimer les tokens de son côté.

    Dans une implémentation plus avancée, on pourrait:
    - Blacklist les tokens dans Redis
    - Invalider les refresh tokens en base
    """
    # Pour l'instant, juste retourner 204
    # Le client supprimera les tokens
    return None
