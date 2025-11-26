#!/bin/bash

# Script pour vérifier le statut de l'application

echo "📊 STATUT DE L'APPLICATION GEO"
echo "==============================="
echo ""

# Statut des services
echo "🔧 Services (Supervisor):"
sudo supervisorctl status

echo ""
echo "💾 Utilisation disque:"
du -sh /app/backend /app/frontend /app/data 2>/dev/null

echo ""
echo "📁 Fichiers temporaires:"
TEMP_FILES=$(find /app/backend -name "queries_config_*.json" -o -name "visibility_results_*.json" 2>/dev/null | wc -l)
echo "  - Fichiers JSON temporaires: $TEMP_FILES"

if [ -d "/app/backend/cache" ]; then
    CACHE_FILES=$(find /app/backend/cache -name "*.json" 2>/dev/null | wc -l)
    echo "  - Fichiers cache: $CACHE_FILES"
fi

if [ -d "/app/backend/reports" ]; then
    REPORTS=$(find /app/backend/reports -type f 2>/dev/null | wc -l)
    echo "  - Rapports générés: $REPORTS"
fi

echo ""
echo "🗄️  Base de données:"
if [ -f "/app/data/geo_history.db" ]; then
    DB_SIZE=$(du -h /app/data/geo_history.db | cut -f1)
    echo "  - Taille: $DB_SIZE"
else
    echo "  - Base de données non trouvée"
fi

echo ""
echo "🌐 Santé de l'API:"
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "  ✅ Backend API est accessible"
else
    echo "  ❌ Backend API n'est pas accessible"
fi

echo ""
echo "💡 Commandes utiles:"
echo "  - Redémarrer les services: sudo supervisorctl restart all"
echo "  - Voir les logs backend: tail -f /var/log/supervisor/backend.*.log"
echo "  - Nettoyer les fichiers temporaires: ./scripts/cleanup.sh"
