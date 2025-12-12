# GEO Backend - API FastAPI

Backend complet pour GEO (Generative Engine Optimization)

## 🚀 Stack

- **Framework**: FastAPI 0.110.1
- **Base de données**: PostgreSQL (SQLAlchemy 2.0)
- **Auth**: JWT (python-jose)
- **Validation**: Pydantic v2
- **Migrations**: Alembic

## 📦 Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

Copier `.env.example` vers `.env` et configurer :

```bash
cp .env.example .env
```

Variables importantes :
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret pour JWT tokens
- `ANTHROPIC_API_KEY`: Clé API Claude
- `OPENAI_API_KEY`: Clé API OpenAI

## 🗄️ Base de données

### Créer la base de données

```bash
# Avec PostgreSQL installé
createdb geo_production
```

### Migrations

```bash
# Générer une migration initiale
alembic revision --autogenerate -m "Initial migration"

# Appliquer les migrations
alembic upgrade head
```

## 🏃 Démarrage

### Mode développement

```bash
# Avec auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Ou simplement :

```bash
python main.py
```

### Mode production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 Documentation API

Une fois l'API démarrée :

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔐 Authentification

Tous les endpoints (sauf `/auth/*`) nécessitent un JWT token :

```bash
# 1. S'enregistrer
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}

# 2. Se connecter
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Réponse :
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}

# 3. Utiliser le token
Authorization: Bearer eyJ...
```

## 📡 Endpoints principaux

### Authentication (`/api/auth`)
- `POST /register` - Créer un compte
- `POST /login` - Se connecter
- `POST /refresh` - Rafraîchir le token
- `POST /logout` - Se déconnecter

### Users (`/api/users`)
- `GET /me` - Profil utilisateur
- `PUT /me` - Mettre à jour le profil
- `GET /me/subscription` - Voir sa subscription

### Analyses (`/api/analyses`)
- `POST /` - Créer une analyse
- `GET /` - Lister ses analyses
- `GET /{id}` - Détails d'une analyse
- `GET /{id}/status` - Status (polling)
- `DELETE /{id}` - Supprimer une analyse

### Reports (`/api/reports`)
- `GET /{analysis_id}` - Récupérer un rapport
- `POST /{analysis_id}/export` - Exporter (PDF, CSV, etc.)

### Admin (`/api/admin`) - Super admin seulement
- `GET /users` - Tous les users
- `GET /analyses` - Toutes les analyses
- `PUT /users/{id}/subscription` - Modifier subscription
- `GET /stats` - Statistiques globales

## 📊 Structure

```
backend_new/
├── main.py              # Point d'entrée FastAPI
├── config.py            # Configuration
├── database.py          # SQLAlchemy setup
├── dependencies.py      # Dependencies injection
├── models/              # Modèles SQLAlchemy (16 tables)
├── schemas/             # Schémas Pydantic
├── routers/             # Routes API
├── utils/               # Utilitaires (auth, etc.)
├── migrations/          # Alembic migrations
└── requirements.txt
```

## 🧪 Tests

```bash
# Installer pytest
pip install pytest pytest-asyncio

# Lancer les tests
pytest
```

## 📝 Notes

- Les endpoints admin nécessitent le rôle `super_admin`
- Les limites d'analyse dépendent du forfait (FREE/PRO/BUSINESS)
- Les analyses sont créées en status `pending` (background task à implémenter)
- Les rapports sont générés automatiquement (à implémenter)

## 🔄 Prochaines étapes

- [ ] Implémenter Celery pour analyses asynchrones
- [ ] Implémenter Redis pour cache
- [ ] Implémenter génération de rapports (PDF, CSV)
- [ ] Tests unitaires et d'intégration
- [ ] Rate limiting par forfait
