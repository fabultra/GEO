# 🏗️ ARCHITECTURE GEO 2.0 - NOUVELLE STRUCTURE

## 📊 Vue d'ensemble

Cette nouvelle architecture remplace complètement l'ancien système MongoDB+React CRA par une stack moderne PostgreSQL+Next.js 14.

**Date de création**: 2025-12-12
**Version**: 2.0.0
**Status**: ✅ Phase 1 complète (Préparation)

---

## 📁 Structure du projet

```
GEO/
├── backend_new/              # 🐍 Backend FastAPI + PostgreSQL
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration centralisée
│   ├── database.py          # SQLAlchemy setup
│   ├── dependencies.py      # Dependencies injection
│   │
│   ├── models/              # 📊 Modèles SQLAlchemy (16 tables)
│   │   ├── user.py
│   │   ├── subscription.py
│   │   ├── website.py
│   │   ├── analysis.py
│   │   ├── crawl_data.py
│   │   ├── semantic.py
│   │   ├── question.py
│   │   ├── llm_test.py
│   │   ├── competitor.py
│   │   ├── recommendation.py
│   │   ├── content.py
│   │   ├── learning.py
│   │   ├── report.py
│   │   └── api_usage.py
│   │
│   ├── schemas/             # Schémas Pydantic (à créer)
│   ├── routers/             # Routes API (à créer)
│   ├── modules/             # Logique métier (à migrer)
│   ├── services/            # Services externes (à migrer)
│   ├── utils/               # Utilitaires (à migrer)
│   ├── tasks/               # Celery tasks (à créer)
│   ├── migrations/          # Alembic migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
│
├── frontend_new/            # ⚛️ Frontend Next.js 14 + TypeScript
│   ├── app/                 # App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── login/
│   │   ├── register/
│   │   ├── dashboard/
│   │   ├── admin/
│   │   └── api/
│   │
│   ├── components/          # Composants React
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/
│   │   ├── auth/
│   │   ├── analysis/
│   │   └── admin/
│   │
│   ├── lib/                 # Bibliothèques
│   │   ├── utils.ts
│   │   └── api.ts           # API client
│   │
│   ├── hooks/               # Custom hooks (à créer)
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   │
│   ├── styles/
│   │   └── globals.css
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   └── .env.example
│
├── backend/                 # ⚠️ Ancien backend (référence)
├── frontend/                # ⚠️ Ancien frontend (référence)
├── DIAGNOSTIC_COMPLET.md    # Rapport d'analyse initial
└── ARCHITECTURE_NOUVELLE.md # Ce fichier
```

---

## 🗄️ SCHÉMA BASE DE DONNÉES POSTGRESQL

### Tables (16 au total)

#### 1. **users**
Utilisateurs de l'application
- `id` (UUID, PK)
- `email` (unique)
- `password_hash`
- `first_name`, `last_name`
- `role` ('super_admin', 'client')
- `is_active`
- Timestamps

#### 2. **subscriptions**
Abonnements et forfaits
- `id` (UUID, PK)
- `user_id` (FK → users)
- `plan_type` ('free', 'pro', 'business')
- `status` ('active', 'cancelled', 'expired')
- `monthly_analyses_limit`
- `analyses_used`
- `price_monthly`
- Dates et timestamps

#### 3. **websites**
Sites web analysés
- `id` (UUID, PK)
- `user_id` (FK → users)
- `url`, `domain`
- `language_detected`, `is_bilingual`, `is_quebec_brand`
- `business_type`
- Timestamps

#### 4. **analyses**
Analyses complètes GEO
- `id` (UUID, PK)
- `website_id` (FK → websites)
- `user_id` (FK → users)
- `status`, `plan_type`
- **Scores** (global_score + 10 scores détaillés)
- Métadonnées (pages_crawled, questions_generated, etc.)
- Timestamps

#### 5. **crawl_data**
Données du crawl par page
- `id` (UUID, PK)
- `website_id` (FK), `analysis_id` (FK)
- `url`, `page_level`
- `title`, `meta_description`
- `h1`, `h2`, `h3` (ARRAY)
- `content_text`, `content_length`
- Schema.org, liens, images

#### 6. **semantic_universe**
Univers sémantique du site
- `id` (UUID, PK)
- `website_id` (FK), `analysis_id` (FK)
- `keywords`, `topics`, `entities` (JSONB)
- `themes` (ARRAY)
- `business_type_detected`
- `semantic_clusters` (JSONB)

#### 7. **generated_questions**
Questions générées pour tests LLM
- `id` (UUID, PK)
- `analysis_id` (FK)
- `question`, `question_type`, `language`
- `relevance_score`

#### 8. **llm_test_results**
Résultats des tests dans les LLMs
- `id` (UUID, PK)
- `analysis_id` (FK), `question_id` (FK)
- `llm_provider`, `llm_model`
- `query_text`, `response_text`
- `brand_mentioned`, `brand_position`
- `competitors_mentioned` (ARRAY)
- `citations_count`, `response_quality_score`

#### 9. **competitors**
Compétiteurs découverts
- `id` (UUID, PK)
- `analysis_id` (FK), `website_id` (FK)
- `competitor_domain`, `competitor_url`
- `discovery_method`
- `mention_count`, `avg_position`, `relevance_score`

#### 10. **competitor_analyses**
Analyses des compétiteurs
- `id` (UUID, PK)
- `competitor_id` (FK), `analysis_id` (FK)
- **Scores** (global_score + 6 scores)
- **Gap analysis**: `gap_global`, `strengths`, `weaknesses`, `opportunities`

#### 11. **technical_recommendations**
Recommandations techniques avec code
- `id` (UUID, PK)
- `analysis_id` (FK)
- `recommendation_type` ('schema_org', 'meta_tags', etc.)
- `page_url`, `priority`
- `code_snippet`, `implementation_notes`
- `estimated_impact`

#### 12. **optimized_content**
Contenu optimisé généré (BUSINESS)
- `id` (UUID, PK)
- `analysis_id` (FK)
- `page_url`, `page_level`
- `optimized_title`, `optimized_meta_description`, `optimized_h1`, `optimized_content`
- `optimized_faq` (JSONB)
- `internal_links_suggestions`, `keywords_targeted`

#### 13. **learning_data**
Données d'apprentissage continu
- `id` (UUID, PK)
- `industry`, `business_type`, `pattern_type`
- `pattern_data` (JSONB)
- `success_rate`, `usage_count`

#### 14. **reports**
Rapports exportés
- `id` (UUID, PK)
- `analysis_id` (FK), `user_id` (FK)
- `report_type` ('pdf', 'json', 'csv', 'html')
- `file_path`, `file_size`

#### 15. **api_usage_logs**
Tracking des coûts API
- `id` (UUID, PK)
- `user_id` (FK), `analysis_id` (FK)
- `api_provider`, `endpoint`
- `tokens_input`, `tokens_output`, `cost_usd`
- `response_time_ms`

---

## 🔐 SYSTÈME D'AUTHENTIFICATION

### JWT Tokens
- **Access token**: 60 minutes
- **Refresh token**: 30 jours
- Algorithme: HS256

### Rôles
- **super_admin** (Fabien)
  - Accès à tout
  - Dashboard admin complet
  - Mode test universel
  - Gestion users & subscriptions

- **client**
  - Accès à ses propres analyses
  - Dashboard personnel
  - Limites selon forfait

### Forfaits

**FREE**:
- 1 analyse/mois
- Score global seulement
- Pas de compétiteurs
- Pas de code technique

**PRO** (1500$ CAD/mois):
- 5 analyses/mois
- Scores détaillés
- Top 5 compétiteurs
- Code technique complet
- Gap analysis

**BUSINESS** (5000$ CAD/mois):
- 20 analyses/mois
- Tout du PRO +
- Top 10 compétiteurs
- Contenu optimisé généré
- API access
- White-label reports

---

## 🛠️ STACK TECHNIQUE

### Backend
- **Framework**: FastAPI 0.110.1
- **Base de données**: PostgreSQL (via SQLAlchemy 2.0)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Cache**: Redis
- **Queue**: Celery + Redis
- **Auth**: JWT (python-jose)
- **Validation**: Pydantic v2
- **API IA**: Anthropic, OpenAI
- **Reports**: ReportLab, python-docx, weasyprint

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5
- **UI**: Radix UI (shadcn/ui)
- **Styling**: Tailwind CSS 3.4
- **Forms**: React Hook Form + Zod
- **State**: Zustand
- **HTTP**: Axios
- **Charts**: Recharts

### Infrastructure (cible)
- **Hosting**: Railway
- **DB**: Railway PostgreSQL 15
- **Cache**: Railway Redis
- **Domaines**:
  - Frontend: geo.sekoia.ca
  - Backend API: api-geo.sekoia.ca

---

## 🚀 ÉTAT ACTUEL - PHASE 1 COMPLÉTÉE

### ✅ Complété

**Backend**:
- [x] Structure complète créée
- [x] 15 modèles SQLAlchemy (16 tables)
- [x] Configuration centralisée (config.py)
- [x] Setup SQLAlchemy (database.py)
- [x] Point d'entrée FastAPI (main.py)
- [x] Dependencies injection (dependencies.py)
- [x] Setup Alembic (migrations)
- [x] requirements.txt
- [x] .env.example

**Frontend**:
- [x] Structure Next.js 14 créée
- [x] Configuration TypeScript
- [x] Setup Tailwind CSS + shadcn/ui
- [x] Layout principal
- [x] API client (lib/api.ts)
- [x] Types TypeScript
- [x] Utilities
- [x] package.json
- [x] .env.example

**Documentation**:
- [x] DIAGNOSTIC_COMPLET.md (analyse préliminaire)
- [x] ARCHITECTURE_NOUVELLE.md (ce fichier)

### ⏳ À faire (Phases 2-8)

**Phase 2-3** (Backend Core + Modules):
- [ ] Schémas Pydantic
- [ ] Routes API (auth, users, analyses, reports, admin)
- [ ] Migration modules depuis ancien backend
- [ ] Tests unitaires

**Phase 4** (Celery + Redis):
- [ ] Setup Celery
- [ ] Tasks analyses asynchrones
- [ ] Cache Redis
- [ ] Rate limiting

**Phase 5** (Frontend):
- [ ] Toutes les pages (login, dashboard, admin, etc.)
- [ ] Composants UI
- [ ] WebSocket progression
- [ ] Tests composants

**Phase 6-8** (Intégration + Déploiement):
- [ ] Frontend ↔ Backend connection
- [ ] Tests E2E
- [ ] Déploiement Railway
- [ ] Documentation finale

---

## 📋 PROCHAINES ÉTAPES

**Immédiat**:
1. Committer Phase 1
2. Démarrer Phase 2 (Backend Core)
3. Créer schémas Pydantic
4. Créer routes auth + users

**Court terme**:
- Migrer modules de l'ancien backend
- Fixer tous les bugs identifiés
- Implémenter auth JWT complète

---

## 🔗 Liens utiles

- **Diagnostic initial**: [DIAGNOSTIC_COMPLET.md](./DIAGNOSTIC_COMPLET.md)
- **Ancien backend**: `./backend/`
- **Ancien frontend**: `./frontend/`
- **Nouveau backend**: `./backend_new/`
- **Nouveau frontend**: `./frontend_new/`

---

**Auteur**: Claude Code Agent
**Date**: 2025-12-12
**Version**: 2.0.0 - Phase 1
**Status**: ✅ PHASE 1 COMPLÈTE
