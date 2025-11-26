#!/bin/bash

# Script de nettoyage automatique des fichiers temporaires
# Usage: ./scripts/cleanup.sh [days]

DAYS=${1:-7}  # Par défaut 7 jours
BACKEND_DIR="/app/backend"

echo "🧹 Nettoyage des fichiers temporaires (> $DAYS jours)..."

# Fonction pour supprimer les fichiers anciens
cleanup_pattern() {
    local pattern=$1
    local dir=$2
    local count=0
    
    find "$dir" -name "$pattern" -type f -mtime +$DAYS -print0 | while IFS= read -r -d '' file; do
        echo "  Suppression: $(basename "$file")"
        rm -f "$file"
        ((count++))
    done
    
    return $count
}

# Nettoyage des fichiers JSON temporaires
echo "📄 Nettoyage des fichiers JSON temporaires..."
find "$BACKEND_DIR" -name "queries_config_*.json" -type f -mtime +$DAYS -delete
find "$BACKEND_DIR" -name "visibility_results_*.json" -type f -mtime +$DAYS -delete

# Nettoyage du cache
if [ -d "$BACKEND_DIR/cache" ]; then
    echo "💾 Nettoyage du cache..."
    find "$BACKEND_DIR/cache" -name "*.json" -type f -mtime +$DAYS -delete
fi

# Nettoyage des anciens rapports (30 jours)
REPORTS_DAYS=30
if [ -d "$BACKEND_DIR/reports" ]; then
    echo "📊 Nettoyage des anciens rapports (> $REPORTS_DAYS jours)..."
    find "$BACKEND_DIR/reports" -type f -mtime +$REPORTS_DAYS -delete
fi

if [ -d "$BACKEND_DIR/dashboards" ]; then
    echo "📈 Nettoyage des anciens dashboards (> $REPORTS_DAYS jours)..."
    find "$BACKEND_DIR/dashboards" -type f -mtime +$REPORTS_DAYS -delete
fi

# Statistiques finales
echo ""
echo "✅ Nettoyage terminé!"
echo "📊 Espace disque libéré:"
du -sh "$BACKEND_DIR" 2>/dev/null

echo ""
echo "💡 Conseil: Ajoutez ce script à un cron pour automatiser le nettoyage"
echo "   Exemple: 0 2 * * * /app/scripts/cleanup.sh 7"
