#!/bin/bash
# ==============================================================================
# SCRIPT DE DÉPLOIEMENT & MISE À JOUR RAPIDE - AGROSEDAM (CPANEL)
# ==============================================================================

set -e

echo "🚀 [1/4] Installation / Mise à jour des dépendances..."
pip install -r requirements.txt

echo "🔄 [2/4] Application des migrations de base de données..."
python manage.py migrate --noinput

echo "📦 [3/4] Collecte des fichiers statiques (Collectstatic)..."
python manage.py collectstatic --noinput

echo "♻️ [4/4] Redémarrage de Phusion Passenger..."
mkdir -p tmp
touch tmp/restart.txt

echo "✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS SUR CPANEL !"
