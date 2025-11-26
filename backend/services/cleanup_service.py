"""
Service de nettoyage automatique des fichiers temporaires
Évite l'accumulation de fichiers
"""
import logging
import time
from pathlib import Path
from typing import Dict

from config import (
    ROOT_DIR,
    CACHE_DIR,
    REPORTS_DIR,
    DASHBOARDS_DIR,
    CLEANUP_TEMP_FILES_DAYS,
    CLEANUP_REPORTS_DAYS,
    CLEANUP_CACHE_DAYS
)

logger = logging.getLogger(__name__)


class CleanupService:
    """Service de nettoyage automatique des fichiers temporaires"""
    
    def __init__(self):
        self.backend_dir = ROOT_DIR
        self.cache_dir = CACHE_DIR
        self.reports_dir = REPORTS_DIR
        self.dashboards_dir = DASHBOARDS_DIR
    
    def cleanup_temp_files(self, days: int = CLEANUP_TEMP_FILES_DAYS) -> int:
        """
        Supprime les fichiers JSON temporaires > X jours
        
        Args:
            days: Nombre de jours après lesquels supprimer
            
        Returns:
            Nombre de fichiers supprimés
        """
        patterns = [
            "queries_config_*.json",
            "visibility_results_*.json",
            "temp_*.json"
        ]
        
        deleted_count = 0
        cutoff_time = time.time() - (days * 86400)
        
        for pattern in patterns:
            for file in self.backend_dir.glob(pattern):
                try:
                    if file.stat().st_mtime < cutoff_time:
                        file.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted temp file: {file.name}")
                except Exception as e:
                    logger.error(f"Failed to delete {file.name}: {e}")
        
        if deleted_count > 0:
            logger.info(f"🗑️  Deleted {deleted_count} temporary files (>{days} days)")
        
        return deleted_count
    
    def cleanup_cache(self, days: int = CLEANUP_CACHE_DAYS) -> int:
        """
        Supprime les fichiers de cache > X jours
        
        Args:
            days: Nombre de jours après lesquels supprimer
            
        Returns:
            Nombre de fichiers supprimés
        """
        if not self.cache_dir.exists():
            return 0
        
        deleted_count = 0
        cutoff_time = time.time() - (days * 86400)
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted cache file: {cache_file.name}")
            except Exception as e:
                logger.error(f"Failed to delete cache {cache_file.name}: {e}")
        
        if deleted_count > 0:
            logger.info(f"🗑️  Deleted {deleted_count} cache files (>{days} days)")
        
        return deleted_count
    
    def cleanup_old_reports(self, days: int = CLEANUP_REPORTS_DAYS) -> int:
        """
        Supprime les anciens rapports > X jours
        
        Args:
            days: Nombre de jours après lesquels supprimer
            
        Returns:
            Nombre de fichiers supprimés
        """
        deleted_count = 0
        cutoff_time = time.time() - (days * 86400)
        
        directories = [self.reports_dir, self.dashboards_dir]
        
        for directory in directories:
            if not directory.exists():
                continue
            
            for file in directory.glob("*"):
                try:
                    if file.is_file() and file.stat().st_mtime < cutoff_time:
                        file.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted report: {file.name}")
                except Exception as e:
                    logger.error(f"Failed to delete report {file.name}: {e}")
        
        if deleted_count > 0:
            logger.info(f"🗑️  Deleted {deleted_count} old reports (>{days} days)")
        
        return deleted_count
    
    def cleanup_all(self, 
                    temp_days: int = CLEANUP_TEMP_FILES_DAYS,
                    cache_days: int = CLEANUP_CACHE_DAYS,
                    reports_days: int = CLEANUP_REPORTS_DAYS) -> Dict[str, int]:
        """
        Exécute tous les nettoyages
        
        Args:
            temp_days: Jours pour fichiers temporaires
            cache_days: Jours pour cache
            reports_days: Jours pour rapports
            
        Returns:
            Dictionnaire avec le nombre de fichiers supprimés par catégorie
        """
        logger.info("🧹 Starting automatic cleanup...")
        
        results = {
            'temp_files': self.cleanup_temp_files(temp_days),
            'cache': self.cleanup_cache(cache_days),
            'reports': self.cleanup_old_reports(reports_days)
        }
        
        total = sum(results.values())
        logger.info(f"✅ Cleanup complete: {total} total files deleted")
        
        return results
    
    def get_cleanup_stats(self) -> Dict[str, any]:
        """
        Retourne des statistiques sur les fichiers nettoyables
        
        Returns:
            Dictionnaire avec les stats
        """
        def count_and_size(directory: Path, pattern: str = "*"):
            if not directory.exists():
                return 0, 0
            files = list(directory.glob(pattern))
            count = len(files)
            size = sum(f.stat().st_size for f in files if f.is_file())
            return count, size
        
        # Compter les fichiers temporaires
        temp_count = 0
        temp_size = 0
        for pattern in ["queries_config_*.json", "visibility_results_*.json", "temp_*.json"]:
            c, s = count_and_size(self.backend_dir, pattern)
            temp_count += c
            temp_size += s
        
        # Cache
        cache_count, cache_size = count_and_size(self.cache_dir, "*.json")
        
        # Reports
        reports_count, reports_size = count_and_size(self.reports_dir)
        dashboards_count, dashboards_size = count_and_size(self.dashboards_dir)
        
        return {
            'temp_files': {
                'count': temp_count,
                'size_mb': round(temp_size / (1024 * 1024), 2)
            },
            'cache': {
                'count': cache_count,
                'size_mb': round(cache_size / (1024 * 1024), 2)
            },
            'reports': {
                'count': reports_count + dashboards_count,
                'size_mb': round((reports_size + dashboards_size) / (1024 * 1024), 2)
            },
            'total_cleanable_mb': round(
                (temp_size + cache_size + reports_size + dashboards_size) / (1024 * 1024), 2
            )
        }


# Instance globale
cleanup_service = CleanupService()
