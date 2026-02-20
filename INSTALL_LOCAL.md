# 🚀 Guide déploiement local - UpdateEngine Modern UI

Ce guide te permet de lancer l'interface moderne d'UpdateEngine sur ta machine locale en quelques minutes, avec ta base MariaDB existante.

---

## ✅ Prérequis

| Outil | Version minimale | Vérification |
|---|---|---|
| Python | 3.10+ | `python --version` |
| pip | 23+ | `pip --version` |
| MariaDB / MySQL | 10.5+ | `mysql --version` |
| Git | n'importe | `git --version` |

> Redis est **optionnel** en local. Le serveur démarrera sans.

---

## 📥 1. Cloner le repo

```bash
git clone https://github.com/Tronos83170/updatengine-server.git
cd updatengine-server
```

---

## 🐍 2. Créer l'environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 3. Installer les dépendances

```bash
# Avec MariaDB (production)
pip install -r requirements/pip-packages.txt

# OU avec SQLite (test rapide sans MariaDB)
pip install -r requirements/pip-packages-sqlite.txt
```

---

## ⚙️ 4. Configurer l'environnement

### Copier le fichier d'exemple

```bash
cp .env.example .env
```

### Éditer `.env` avec tes valeurs

```env
# --- SECURITE ---
SECRET_KEY=change-moi-avec-une-vraie-cle-secrete-longue
DEBUG=True

# --- SERVEUR ---
SERVER_NAME=localhost
PORT=8000
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# --- BASE DE DONNEES MariaDB ---
DB_HOST=localhost
DB_PORT=3306
DB_NAME=updatengine          # nom de ta base UE
DB_USER=ue_user              # ton utilisateur MariaDB
DB_PASSWORD=ton_mot_de_passe

# --- LANGUE ---
LANGUAGE_CODE=fr
TZ=Europe/Paris

# --- REDIS (optionnel en local) ---
# REDIS_URL=redis://localhost:6379/0
# CACHE_TIMEOUT=300

# --- EMAIL (optionnel) ---
# EMAIL_HOST=localhost
# EMAIL_PORT=25
```

> ⚠️ **Si tu n'as pas Redis**, ajoute ça dans `updatengine/settings_local.py` (crée le fichier s'il n'existe pas) :
> ```python
> CACHES = {'default': {'BACKEND': 'django.core.cache.backends.LocMemCache'}}
> SESSION_ENGINE = 'django.contrib.sessions.backends.db'
> ```

---

## 🖳️ 5. Générer `settings.py` depuis le template

```bash
cp updatengine/settings.py.in updatengine/settings.py
```

> Le fichier `settings.py.in` lit automatiquement le `.env` via `django-environ`.

---

## 🗄️ 6. Appliquer les migrations

```bash
python manage.py migrate
```

Si tu utilises une base **existante** d'UpdateEngine, les tables sont déjà présentes, les migrations ne feront que vérifier.

---

## 👤 7. Créer un superutilisateur (si nouvelle base)

```bash
python manage.py createsuperuser
```

---

## 🎮 8. Lancer le serveur de développement

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🌐 9. Accéder à l'interface

| URL | Description |
|---|---|
| `http://localhost:8000/modern/dashboard/` | 🏠 **Dashboard moderne** |
| `http://localhost:8000/modern/inventory/` | 🖥️ Parc machines |
| `http://localhost:8000/modern/deploy/` | 🚀 Déploiements |
| `http://localhost:8000/modern/alerts/` | 🔔 **Alertes & notifications** |
| `http://localhost:8000/admin/` | ⚙️ Administration Django |
| `http://localhost:8000/` | Interface UE classique |

---

## 🔧 Dépannage courant

### Erreur `django_redis` / Redis non disponible

Crée `updatengine/settings_local.py` :
```python
# Désactive Redis pour le développement local
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.LocMemCache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

### Erreur `mysqlclient` sur Windows

```bash
pip install mysqlclient --no-binary mysqlclient
# OU installer via : https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
```

### Erreur `No module named 'updatengine.settings'`

```bash
# Vérifie que settings.py existe
ls updatengine/settings.py
# Sinon :
cp updatengine/settings.py.in updatengine/settings.py
```

### Pages statiques (CSS/JS) non chargées

```bash
python manage.py collectstatic --noinput
```

En mode `DEBUG=True`, les fichiers statiques sont servis automatiquement.

### Erreur `CSRF` sur les formulaires

Vérifie dans `.env` :
```env
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```

---

## 🐳 Alternative : lancement via Docker (optionnel)

Si tu as Docker installé :

```bash
docker compose up -d
# Puis accéder à http://localhost:8000/modern/dashboard/
```

---

## 📝 Notes développement

- Les templates modernes sont dans `updatengine/templates/modern/`
- Les vues modernes sont dans `updatengine/views_modern.py`
- Les URLs modernes : `updatengine/urls_modern.py` (namespace `modern:`)
- Pour activer le rechargement automatique : `python manage.py runserver` (déjà inclus)
- Tailwind CSS et HTMX sont chargés via CDN — **pas besoin de build**

---

*Généré automatiquement pour le projet UpdateEngine Modern UI*
