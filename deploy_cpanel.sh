#!/bin/bash
# ==============================================================================
# SCRIPT DE DÉPLOIEMENT & MISE À JOUR RAPIDE - AGROSEDAM (CPANEL)
# ==============================================================================

set -e

# Activation automatique de l'environnement virtuel Python 3.11 cPanel
if [ -f "/home/$USER/virtualenv/repositories/Agrosedam/3.11/bin/activate" ]; then
    echo "🐍 Activation de l'environnement virtuel Python 3.11..."
    source "/home/$USER/virtualenv/repositories/Agrosedam/3.11/bin/activate"
fi

echo "🚀 [1/5] Installation / Mise à jour des dépendances..."
pip install -r requirements.txt

echo "🔄 [2/5] Application des migrations de base de données..."
python manage.py migrate --noinput

echo "📦 [3/5] Collecte des fichiers statiques (Collectstatic)..."
python manage.py collectstatic --noinput

# Synchronisation directe avec le DocumentRoot du sous-domaine s'il existe
if [ -d "/home/$USER/agrosedam.tdjel.com" ]; then
    echo "🌐 [4/5] Copie des fichiers statiques vers le webroot du sous-domaine..."
    mkdir -p /home/$USER/agrosedam.tdjel.com/static
    cp -ru staticfiles/* /home/$USER/agrosedam.tdjel.com/static/ 2>/dev/null || true
fi

echo "🔒 [5/5] Ajustement des permissions et redémarrage..."
find /home/$USER/repositories/Agrosedam -type d -exec chmod 755 {} + 2>/dev/null || true
find /home/$USER/repositories/Agrosedam -type f -exec chmod 644 {} + 2>/dev/null || true
mkdir -p tmp
touch tmp/restart.txt

echo "========================================================"
echo "✅ DÉPLOIEMENT & DESIGNS MIS À JOUR AVEC SUCCÈS SUR CPANEL !"
echo "========================================================"
