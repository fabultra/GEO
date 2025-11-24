# GEO Platform - Transformation Complète

## Vue d'ensemble
Transformation de l'application en plateforme 100% Generative Engine Optimization (GEO).
Suppression de tous les éléments SEO local inutiles. Focus absolu sur la performance dans les moteurs génératifs (ChatGPT, Claude, Perplexity, Gemini, AI Overviews).

## Fichiers Modifiés

### Backend Core
- `server.py` - Modèle Score refactoré avec answerability, pondération GEO
- `scoring_grids.py` - Purge du SEO local, focus schémas GEO (FAQPage, Article, HowTo)
- `competitive_intelligence.py` - Analyse 5 compétiteurs, multi-pages, GEO Power Score
- `token_analyzer.py` - Labels descriptifs, truncation_risk, pas de jugement qualité
- `visibility_tester_v2.py` - Documentation GEO focus
- `data_gap_detector.py` - Documentation GEO focus
- `word_report_generator.py` - Rapport GEO enrichi

### Frontend
- `ReportPage.js` - Affichage des nouvelles métriques GEO
- `dashboard_visibility_generator.py` - Dashboard enrichi compétition GEO

## Nouvelle Structure du Modèle Score

```python
class Score(BaseModel):
    structure: float = 0.0          # Structure sémantique pour IA
    answerability: float = 0.0      # Capacité à répondre clairement (NOUVEAU)
    readability: float = 0.0        # Lisibilité machine/IA
    eeat: float = 0.0              # Expertise, Autorité, Fiabilité
    educational: float = 0.0        # Valeur éducative du contenu
    thematic: float = 0.0          # Cohérence thématique
    aiOptimization: float = 0.0    # Optimisation spécifique IA
    visibility: float = 0.0         # Visibilité réelle dans les IA
    infoDensity: float = 0.0       # Métrique technique (plus dans score global)
    global_score: float = 0.0      # Score GEO global

@staticmethod
def calculate_weighted_score(scores: dict) -> float:
    weights = {
        "structure": 0.15,
        "answerability": 0.20,      # Priorité maximale
        "readability": 0.10,
        "eeat": 0.15,
        "educational": 0.15,
        "thematic": 0.10,
        "aiOptimization": 0.10,
        "visibility": 0.05
    }
    # infoDensity n'est PLUS dans le calcul
```

## Structure Competitive Intelligence

```json
{
  "competitors_analyzed": 5,
  "pages_analyzed": 25,
  "confidence_level": "HIGH",
  "analyses": [
    {
      "domain": "competitor.com",
      "main_url": "https://competitor.com",
      "pages_analyzed": [
        {
          "url": "...",
          "word_count": 2500,
          "h1_count": 1,
          "h2_count": 8,
          "has_direct_answer": true,
          "has_tldr": true,
          "stats_count": 15,
          "faq_count": 10,
          "schema_count": 3
        }
      ],
      "aggregate": {
        "total_word_count": 12500,
        "avg_word_count": 2500,
        "total_stats": 75,
        "avg_stats_per_page": 15,
        "total_faq": 50,
        "schema_presence_rate": 0.80,
        "direct_answer_rate": 0.60,
        "tldr_rate": 0.40
      },
      "llm_visibility": {
        "overall": 0.45,
        "by_platform": {...}
      },
      "geo_power_score": 8.5
    }
  ],
  "comparative_metrics": {
    "NOUS": {...},
    "AVERAGE_COMPETITORS": {...},
    "GAP": {...}
  },
  "actionable_insights": [...]
}
```

## Structure Token Analysis

```json
{
  "global_analysis": {
    "avg_tokens": 1250,
    "avg_density": 0.018,
    "density_rating": "DENSITÉ MOYENNE",
    "truncation_risk": {
      "token_limit": 8000,
      "pages_will_truncate": 2,
      "risk_level": "MEDIUM"
    },
    "density_explanation": "La densité informationnelle mesure le nombre de faits par rapport au volume de texte. Ce n'est PAS une note de performance GEO. En GEO, le plus important est que les contenus critiques ne soient pas tronqués et restent facilement exploitables par les moteurs génératifs."
  }
}
```

## Changements Clés

### 1. Purge SEO Local
- ❌ Supprimé: Schema.org LocalBusiness
- ❌ Supprimé: Critères NAP (Name, Address, Phone)
- ❌ Supprimé: Google Maps integration
- ❌ Supprimé: Géolocalisation dans scoring

### 2. Focus Schémas GEO
- ✅ Schema.org FAQPage (questions critiques IA)
- ✅ Schema.org Article (contenu éditorial)
- ✅ Schema.org HowTo (guides pratiques)
- ✅ Schema.org QAPage (Q&A structuré)
- ✅ TL;DR / résumés structurés

### 3. Analyse Compétition Renforcée
- Passage de 3 à 5 compétiteurs
- Multi-pages par compétiteur (5 pages internes + page principale)
- GEO Power Score (0-10) basé sur:
  - Visibilité LLM
  - Direct answer rate
  - TL;DR rate
  - Schema presence
  - Stats density
- Comparatif NOUS vs COMPÉTITEURS
- Confidence level (HIGH/MEDIUM/LOW)

### 4. Token Analysis Refactoré
- Labels descriptifs sans jugement qualité
- Truncation risk avec niveaux (HIGH/MEDIUM/LOW)
- Explication claire: densité ≠ qualité GEO
- infoDensity hors du score global

### 5. Dimension Answerability
- Nouvelle dimension prioritaire (20% du score)
- Mesure la capacité du site à répondre clairement
- Basée sur:
  - Présence de réponses directes
  - Structure FAQ
  - TL;DR
  - Paragraphes introductifs clairs

## Métriques GEO Clés

### Par Page
- `has_direct_answer` - Réponse claire dans les premiers paragraphes
- `has_tldr` - Présence d'un résumé TL;DR
- `stats_count` - Nombre de données chiffrées
- `faq_count` - Nombre de Q&A
- `schema_count` - Nombre de schémas structurés
- `lists_count` - Nombre de listes structurées
- `tables_count` - Nombre de tableaux de données

### Agrégé
- `direct_answer_rate` - % de pages avec réponse directe
- `tldr_rate` - % de pages avec TL;DR
- `schema_presence_rate` - % de pages avec schémas
- `avg_stats_per_page` - Richesse en données
- `geo_power_score` - Score GEO global (0-10)

## Exemple JSON Complet (Anonymisé)

```json
{
  "site_url": "https://example.com",
  "scores": {
    "structure": 7.5,
    "answerability": 6.0,
    "readability": 8.0,
    "eeat": 7.0,
    "educational": 8.5,
    "thematic": 7.5,
    "aiOptimization": 6.5,
    "visibility": 0.25,
    "infoDensity": 0.018,
    "global_score": 7.2
  },
  "competitive_intelligence": {
    "competitors_analyzed": 5,
    "pages_analyzed": 28,
    "confidence_level": "HIGH",
    "comparative_metrics": {
      "NOUS": {
        "geo_power_score": 5.5,
        "avg_word_count": 1200,
        "avg_stats_per_page": 5,
        "direct_answer_rate": 0.30,
        "schema_presence_rate": 0.40
      },
      "AVERAGE_COMPETITORS": {
        "geo_power_score": 7.8,
        "avg_word_count": 2300,
        "avg_stats_per_page": 12,
        "direct_answer_rate": 0.65,
        "schema_presence_rate": 0.75
      },
      "GAP": {
        "geo_power_score": -2.3,
        "avg_word_count": -1100,
        "avg_stats_per_page": -7,
        "direct_answer_rate": -0.35,
        "schema_presence_rate": -0.35
      }
    }
  },
  "token_analysis": {
    "global_analysis": {
      "avg_tokens": 1250,
      "density_rating": "DENSITÉ MOYENNE",
      "truncation_risk": {
        "risk_level": "LOW",
        "pages_will_truncate": 0
      }
    }
  }
}
```

## Déclaration GEO

**Cet outil est désormais orienté 100% Generative Engine Optimization (GEO).**

Aucun signal SEO local traditionnel (NAP, LocalBusiness, Google Maps) ne contribue au scoring.
Le focus absolu est sur la performance dans les moteurs génératifs et leur capacité à citer,
recommander et extraire des informations de qualité du site analysé.

Les métriques clés sont:
- Visibilité réelle dans ChatGPT, Claude, Perplexity, Gemini
- Capacité à fournir des réponses claires et directes
- Richesse en données factuelles structurées
- Présence de schémas adaptés aux IA (FAQPage, Article, HowTo)
- Structure optimisée pour l'extraction par LLM

## Status d'Implémentation

### ✅ PHASE 1 - Core GEO Refactoring (COMPLÉTÉ)
- [x] Étape 1: Documentation et docstrings GEO (CompetitiveIntelligence, TokenAnalyzer, VisibilityTesterV2, DataGapDetector, Score)
- [x] Étape 2: Purge SEO local dans scoring_grids.py (LocalBusiness supprimé, schémas GEO ajoutés)
- [x] Étape 3: Refonte modèle Score avec answerability (priorité 20%)
- [x] Étape 3b: calculate_weighted_score refactoré (infoDensity exclus)
- [x] Étape 3c: Refonte _rate_density avec labels descriptifs
- [x] Étape 3d: Ajout truncation_risk et density_explanation

### 🔄 PHASE 2 - Competitive Intelligence 2.0 (À VENIR)
- [ ] Étape 4: Analyse 5 compétiteurs au lieu de 3
- [ ] Étape 5: Multi-pages par compétiteur (_analyze_competitor_page)
- [ ] Étape 6: GEO Power Score (compute_geo_power_score)
- [ ] Étape 8: Confidence level (_compute_confidence_level)

### 🔄 PHASE 3 - Comparatif NOUS vs COMPÉTITEURS (À VENIR)
- [ ] Étape 7: Comparatif NOUS vs COMPÉTITEURS (refonte generate_comparative_table)

### 🔄 PHASE 4-6 - Frontend, Rapports, Validation (À VENIR)
- [ ] Étape 10: Mise à jour frontend et rapports
- [ ] Étape 11: Validation complète

---
Date: 2025-01-XX
Version: 2.0 - GEO Pure
