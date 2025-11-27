"""
Service de cache local avec fichiers JSON
Évite les appels API coûteux pour les analyses récentes
"""
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any, Callable
from functools import wraps

from config import (
    CACHE_DIR,
    CACHE_TTL_HOURS,
    CACHE_ENABLED,
    is_cache_enabled
)

logger = logging.getLogger(__name__)


class CacheService:
    """Service de cache simple basé sur des fichiers JSON"""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.enabled = CACHE_ENABLED
    
    def _get_cache_key_hash(self, key: str) -> str:
        """Génère un hash MD5 pour la clé de cache"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Retourne le chemin du fichier de cache"""
        key_hash = self._get_cache_key_hash(key)
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str, max_age_hours: Optional[int] = None) -> Optional[Any]:
        """
        Récupère une valeur depuis le cache
        
        Args:
            key: Clé de cache
            max_age_hours: Âge maximum en heures (défaut: CACHE_TTL_HOURS)
            
        Returns:
            Valeur cachée ou None si pas trouvée/expirée
        """
        if not self.enabled or not is_cache_enabled():
            return None
        
        max_age = max_age_hours if max_age_hours is not None else CACHE_TTL_HOURS
        cache_file = self._get_cache_file_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            # Vérifier l'âge du fichier
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            age = datetime.now() - file_time
            
            if age > timedelta(hours=max_age):
                # Cache expiré, supprimer
                cache_file.unlink()
                logger.debug(f"Cache expired for key: {key[:50]}...")
                return None
            
            # Lire le cache
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ Cache HIT for key: {key[:50]}...")
                return data.get('value')
                
        except Exception as e:
            logger.warning(f"Failed to read cache for {key[:50]}...: {e}")
            # En cas d'erreur, supprimer le fichier corrompu
            try:
                cache_file.unlink()
            except Exception:
                pass
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Sauvegarde une valeur dans le cache
        
        Args:
            key: Clé de cache
            value: Valeur à cacher (doit être JSON serializable)
            
        Returns:
            True si succès, False sinon
        """
        if not self.enabled or not is_cache_enabled():
            return False
        
        cache_file = self._get_cache_file_path(key)
        
        try:
            data = {
                'key': key,
                'value': value,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Cache SET for key: {key[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write cache for {key[:50]}...: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache
        
        Args:
            key: Clé à supprimer
            
        Returns:
            True si supprimé, False si pas trouvé
        """
        cache_file = self._get_cache_file_path(key)
        
        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.info(f"🗑️  Cache DELETE for key: {key[:50]}...")
                return True
            except Exception as e:
                logger.error(f"Failed to delete cache for {key[:50]}...: {e}")
                return False
        
        return False
    
    def clear_all(self) -> int:
        """
        Vide tout le cache
        
        Returns:
            Nombre de fichiers supprimés
        """
        count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.error(f"Failed to delete {cache_file}: {e}")
        
        logger.info(f"🗑️  Cleared {count} cache files")
        return count
    
    def cleanup_expired(self, max_age_hours: Optional[int] = None) -> int:
        """
        Supprime les fichiers de cache expirés
        
        Args:
            max_age_hours: Âge maximum (défaut: CACHE_TTL_HOURS)
            
        Returns:
            Nombre de fichiers supprimés
        """
        max_age = max_age_hours if max_age_hours is not None else CACHE_TTL_HOURS
        cutoff_time = datetime.now() - timedelta(hours=max_age)
        count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_time:
                    cache_file.unlink()
                    count += 1
            except Exception as e:
                logger.error(f"Failed to cleanup {cache_file}: {e}")
        
        if count > 0:
            logger.info(f"🗑️  Cleaned up {count} expired cache files")
        
        return count
    
    def get_cache_stats(self) -> dict:
        """
        Retourne des statistiques sur le cache
        
        Returns:
            Dictionnaire avec les stats
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'enabled': self.enabled,
            'total_files': len(cache_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }


def cache_result(key_prefix: str, max_age_hours: Optional[int] = None):
    """
    Décorateur pour cacher automatiquement le résultat d'une fonction
    
    Usage:
        @cache_result("analysis", max_age_hours=168)
        async def analyze_site(url: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = CacheService()
            
            # Générer une clé unique basée sur les arguments
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            
            # Vérifier le cache
            cached_value = cache.get(cache_key, max_age_hours)
            if cached_value is not None:
                return cached_value
            
            # Exécuter la fonction
            result = await func(*args, **kwargs)
            
            # Cacher le résultat
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


# Instance globale du cache
cache_service = CacheService()
