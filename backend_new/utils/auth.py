"""
Utilitaires d'authentification
JWT tokens et password hashing
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_EXPIRATION_MINUTES,
    JWT_REFRESH_EXPIRATION_DAYS,
)

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe contre son hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un access token JWT

    Args:
        data: Données à encoder (ex: {"sub": user_id})
        expires_delta: Durée de validité (défaut: JWT_EXPIRATION_MINUTES)

    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Crée un refresh token JWT

    Args:
        data: Données à encoder (ex: {"sub": user_id})

    Returns:
        Refresh token JWT encodé
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_EXPIRATION_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Vérifie et décode un JWT token

    Args:
        token: Token JWT
        token_type: Type attendu ("access" ou "refresh")

    Returns:
        Payload du token si valide, None sinon
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Vérifier le type de token
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None

        return payload

    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extrait l'user_id d'un token

    Args:
        token: Token JWT

    Returns:
        User ID si valide, None sinon
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
