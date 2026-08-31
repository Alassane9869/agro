# Guide de déploiement AgroSedam sur o2switch / cPanel
### Sous-domaine officiel : `agrosedam.tdjel.com`

---

## 1. Prérequis sur cPanel

1. **Sous-domaine créé** : `agrosedam.tdjel.com`
   - Dans cPanel > **Domaines** > **Créer un domaine / sous-domaine**
   - Nom : `agrosedam.tdjel.com`
   - Racine du document (*DocumentRoot*) : `/home/USER/agrosedam.tdjel.com`
2. **Accès Git ou Gestionnaire de fichiers** :
   - Dépôt : `https://github.com/djelikacodeuse/Agrosedam.git`
   - Emplacement du code : `/home/USER/repositories/Agrosedam` (ou `/home/USER/agrosedam`)

---

## 2. Configuration Python (*Setup Python App*)

1. Rendez-vous dans **Setup Python App** dans cPanel.
2. Cliquez sur **Créer une application** (*Create Application*).
3. Renseignez :
   - **Python version** : `3.11` (ou `3.10` / `3.12`)
   - **Application root** : `repositories/Agrosedam` (ou `agrosedam`)
   - **Application URL** : Choisissez `agrosedam.tdjel.com`
   - **Application startup file** : `passenger_wsgi.py`
   - **Application Entry point** : `application`
4. Cliquez sur **Create**.

---

## 3. Installation des paquets & Déploiement

Dans le terminal SSH cPanel ou via l'interface :
```bash
# 1. Activer le virtualenv (copier la commande donnée par cPanel en haut de Setup Python App)
source /home/USER/virtualenv/repositories/Agrosedam/3.11/bin/activate

# 2. Aller dans le dossier
cd /home/USER/repositories/Agrosedam

# 3. Lancer le script de déploiement automatique
bash deploy_cpanel.sh
```

---

## 4. Fichier `.env` en Production

Créer un fichier `.env` dans `/home/USER/repositories/Agrosedam/.env` :
```ini
DJANGO_SECRET_KEY=cle_secrete_ultra_securisee
DEBUG=False
DJANGO_ALLOWED_HOSTS=agrosedam.tdjel.com,www.agrosedam.tdjel.com,tdjel.com,www.tdjel.com,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://agrosedam.tdjel.com,https://www.agrosedam.tdjel.com,https://tdjel.com,https://www.tdjel.com
```

---

## 5. Redémarrer l'application

```bash
mkdir -p tmp && touch tmp/restart.txt
```
L'application est maintenant en ligne et accessible sur **https://agrosedam.tdjel.com** !
