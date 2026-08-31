# 🌱 AgroSedam — Plateforme Intégrée de Gestion Agricole & Élevage

![Django](https://img.shields.io/badge/Django-4.2%20LTS-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![cPanel](https://img.shields.io/badge/cPanel-o2switch%20%2F%20LiteSpeed-FF6C2C?style=for-the-badge&logo=cpanel&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)

**AgroSedam** est une application web complète développée avec **Django** permettant le suivi et la gestion centralisée d'exploitations agricoles et pastorales.

🌐 **Production en ligne :** [https://agrosedam.tdjel.com](https://agrosedam.tdjel.com)

---

## 📑 Table des Matières
1. [Fonctionnalités Principales](#-fonctionnalités-principales)
2. [Structure du Projet](#-structure-du-projet)
3. [Installation & Lancement en Local](#-installation--lancement-en-local)
4. [Déploiement sur cPanel / o2switch (Guide Pas-à-Pas)](#-déploiement-sur-cpanel--o2switch-guide-pas-à-pas)
5. [Variables d'Environnement (.env)](#-variables-denvironnement-env)
6. [Commandes d'Administration Utiles](#-commandes-dadministration-utiles)

---

## ✨ Fonctionnalités Principales

- 🌾 **Gestion des Cultures & Parcelles** : Enregistrement des parcelles, suivi des saisons agricoles, planification des semis et calcul des rendements de récolte.
- 🐄 **Gestion de l'Élevage & Cheptel** : Suivi des animaux (bovins, ovins, caprins), identification par matricule/nom, état de santé et alimentation.
- 🐔 **Aviculture & Couveuses** : Suivi des bandes de volaille, surveillance des incubateurs, taux d'éclosion et alertes de température.
- 🤖 **Assistant Intelligent Intégré** : Module de chat intelligent (`assistant`) pour aider les exploitants sur les diagnostics et bonnes pratiques agronomiques.
- 🔔 **Système de Notifications** : Alertes automatiques pour les tâches critiques, récoltes et interventions d'élevage.
- 👥 **Gestion des Utilisateurs & Sécurité** : Authentification sécurisée, rôles, réinitialisation de mot de passe par email.

---

## 📂 Structure du Projet

```text
Agrosedam/
├── agrosedam/                     # ⚙️ Configuration racine du projet
│   ├── settings.py                # Paramètres (Production & Local avec .env)
│   ├── urls.py                    # Routage global
│   ├── wsgi.py                    # WSGI standard
│   └── asgi.py                    # ASGI
│
├── gestion/                       # 🌾 Application Métier (Cultures & Élevage)
│   ├── models.py                  # Modèles de données
│   ├── views.py                   # Vues & Logique métier
│   ├── forms.py                   # Formulaires
│   ├── urls.py                    # URLs de l'application
│   └── management/commands/       # Commandes personnalisées (seed_data, etc.)
│
├── assistant/                     # 🤖 Application Assistant & IA
│   ├── views.py                   # Vues du chatbot
│   ├── urls.py                    # Routes de l'assistant
│   └── templates/                 # Templates du chat
│
├── templates/                     # 🎨 Templates HTML (Bootstrap / Tailwind)
├── static/                        # 📦 Fichiers statiques (CSS, JS, Images)
├── db.sqlite3                     # 🗄️ Base de données SQLite initiale
│
├── passenger_wsgi.py              # 🚀 Point d'entrée WSGI pour Phusion Passenger (cPanel)
├── requirements.txt               # 📋 Dépendances Python requises
├── deploy_cpanel.sh               # ⚡ Script de déploiement automatique 1-clic
├── .cpanel.yml                    # 🔄 Configuration Git cPanel
├── .env.example                   # 🔒 Modèle des variables d'environnement
└── DEPLOIEMENT_O2SWITCH.md        # 📘 Documentation détaillée du déploiement
```

---

## 💻 Installation & Lancement en Local

### 1. Cloner le projet
```bash
git clone https://github.com/djelikacodeuse/Agrosedam.git
cd Agrosedam
```

### 2. Créer et activer l'environnement virtuel
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations
```bash
python manage.py migrate
```

### 5. Démarrer le serveur de développement
```bash
python manage.py runserver
```
Rendez-vous sur [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 🌐 Déploiement sur cPanel / o2switch (Guide Pas-à-Pas)

### Étape 1 : Créer le sous-domaine
1. Connectez-vous à **cPanel**.
2. Dans la section **Domaines**, créez le sous-domaine : **`agrosedam.tdjel.com`**.
3. Définissez la racine du document vers `/home/USER/agrosedam.tdjel.com`.

### Étape 2 : Cloner le dépôt via Git cPanel
1. Ouvrez **Git™ Version Control** dans cPanel.
2. Cliquez sur **Create** :
   - **Clone URL** : `https://github.com/djelikacodeuse/Agrosedam.git`
   - **Repository Path** : `repositories/Agrosedam`
   - **Repository Name** : `Agrosedam`
3. Cliquez sur **Create**.

### Étape 3 : Créer l'application Python (*Setup Python App*)
1. Dans cPanel, cliquez sur **Setup Python App** (ou *Configuration Python*).
2. Cliquez sur **Create Application** :
   - **Python version** : `3.11` (ou `3.10`)
   - **Application root** : `repositories/Agrosedam`
   - **Application URL** : Sélectionnez `agrosedam.tdjel.com`
   - **Application startup file** : `passenger_wsgi.py`
   - **Application Entry point** : `application`
3. Cliquez sur **Create**.

### Étape 4 : Lancer le script de déploiement automatique
Dans le **Terminal cPanel (SSH)** :
```bash
# Activer le virtualenv de l'application (copier la commande fournie par cPanel)
source /home/USER/virtualenv/repositories/Agrosedam/3.11/bin/activate

# Se placer dans le projet
cd /home/USER/repositories/Agrosedam

# Exécuter le script de déploiement
bash deploy_cpanel.sh
```

---

## 🔒 Variables d'Environnement (.env)

Créez un fichier `.env` à la racine du projet en production (`/home/USER/repositories/Agrosedam/.env`) :

```ini
# Sécurité
DJANGO_SECRET_KEY=votre_cle_secrete_ultra_securisee
DEBUG=False

# Domaines autorisés (HTTPS)
DJANGO_ALLOWED_HOSTS=agrosedam.tdjel.com,www.agrosedam.tdjel.com,tdjel.com,www.tdjel.com,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://agrosedam.tdjel.com,https://www.agrosedam.tdjel.com,https://tdjel.com,https://www.tdjel.com

# Base de données MySQL (Optionnel si vous n'utilisez pas SQLite)
USE_MYSQL=False
# DB_NAME=tdjel_agrosedam
# DB_USER=tdjel_user
# DB_PASSWORD=MotDePasseFort123!
# DB_HOST=localhost
# DB_PORT=3306
```

---

## 🛠️ Commandes d'Administration Utiles

- **Créer un administrateur Django** :
  ```bash
  python manage.py createsuperuser
  ```

- **Générer des données de test** :
  ```bash
  python manage.py seed_data
  ```

- **Redémarrer Phusion Passenger en production** :
  ```bash
  mkdir -p tmp && touch tmp/restart.txt
  ```

---

## 👥 Auteur & Collaboration
- **Développeuse Principale** : [@djelikacodeuse](https://github.com/djelikacodeuse)
- **Projet** : Agrosedam ERP & Plateforme Agro-pastorale
