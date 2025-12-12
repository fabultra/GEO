"""
Dépendances réutilisables pour FastAPI
Authentification, autorisation, validation, etc.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
import logging

from database import get_db
from config import JWT_SECRET, JWT_ALGORITHM

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency pour obtenir l'utilisateur courant depuis le JWT

    Usage:
        @app.get("/protected")
        def protected_route(user = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # TODO: Import User model and fetch from DB
    # from models.user import User
    # user = db.query(User).filter(User.id == user_id).first()
    # if user is None or not user.is_active:
    #     raise credentials_exception
    # return user

    # Temporaire: retourner juste l'ID
    return {"id": user_id}


def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Dependency pour vérifier que l'utilisateur est actif
    """
    # TODO: Vérifier user.is_active
    return current_user


def require_role(required_role: str):
    """
    Dependency factory pour vérifier le rôle de l'utilisateur

    Usage:
        @app.get("/admin")
        def admin_route(user = Depends(require_role("super_admin"))):
            return {"message": "Admin access"}
    """
    def role_checker(current_user = Depends(get_current_active_user)):
        # TODO: Vérifier current_user.role == required_role
        # if current_user.role != required_role:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Insufficient permissions"
        #     )
        return current_user

    return role_checker


def check_subscription_limit(plan_type: str, feature: str):
    """
    Dependency factory pour vérifier les limites de subscription

    Usage:
        @app.post("/analyses")
        def create_analysis(
            user = Depends(get_current_user),
            _check = Depends(check_subscription_limit("analyses", "create"))
        ):
            ...
    """
    def limit_checker(
        current_user = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        # TODO: Implémenter vérification limites
        # - Vérifier subscription de l'utilisateur
        # - Vérifier analyses_used vs monthly_analyses_limit
        # - Vérifier feature disponible dans le plan
        # - Raise HTTPException si limite atteinte
        pass

    return limit_checker


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    """
    Dependency pour obtenir l'utilisateur courant (optionnel)
    Retourne None si pas de token
    Utile pour endpoints publics avec contenu différent si authentifié
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        # TODO: Fetch user from DB
        return {"id": user_id}

    except JWTError:
        return None
