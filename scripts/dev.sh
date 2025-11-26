#!/bin/bash

# Script pour démarrer l'environnement de développement

echo "🚀 Démarrage de l'environnement de développement GEO..."

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "/app/backend" ] || [ ! -d "/app/frontend" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis /app"
    exit 1
fi

# Fonction pour vérifier si un service est en cours d'exécution
check_service() {
    local service=$1
    if supervisorctl status $service | grep -q "RUNNING"; then
        echo "✅ $service est en cours d'exécution"
        return 0
    else
        echo "⚠️  $service n'est pas en cours d'exécution"
        return 1
    fi
}

# Redémarrer les services
echo ""
echo "🔄 Redémarrage des services..."
sudo supervisorctl restart all

sleep 3

# Vérifier le statut
echo ""
echo "📊 Statut des services:"
check_service backend
check_service frontend

# Afficher les logs récents
echo ""
echo "📝 Logs backend (dernières 10 lignes):"
tail -n 10 /var/log/supervisor/backend.err.log 2>/dev/null || echo "Pas d'erreurs"

echo ""
echo "📝 Logs frontend (dernières 10 lignes):"
tail -n 10 /var/log/supervisor/frontend.err.log 2>/dev/null || echo "Pas d'erreurs"

echo ""
echo "✅ Environnement de développement prêt!"
echo "🌐 Backend API: http://localhost:8001/api"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8001/docs"
