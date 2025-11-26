# Méthodologie de Scoring GEO

## Vue d'ensemble

L'outil GEO Analytics utilise une approche hybride combinant **extraction automatisée** de données web et **analyse IA avancée** avec Claude Sonnet 4 pour évaluer la préparation d'un site web aux moteurs génératifs (ChatGPT, Perplexity, Google AI Overviews).

---

## Processus d'analyse en 3 phases

### Phase 1: Crawling et extraction (40% du temps)
```
Entrée: URL du site (ex: https://exemple.com)
↓
Crawler automatique:
  - Respect des délais (0.5s entre requêtes)
  - Limite configurable (CRAWL_MAX_PAGES=50)
  - Extraction de domaine uniquement
  
Données extraites par page:
  ✓ <title>
  ✓ <meta name="description">
  ✓ Balises H1, H2, H3
  ✓ Paragraphes (>50 caractères)
  ✓ JSON-LD (structured data)
  ✓ Liens internes
  ✓ Nombre de mots
```

### Phase 2: Analyse IA avec Claude (30% du temps)
```
Modèle: Claude Sonnet 4 (claude-3-7-sonnet-20250219)
API: Emergent LLM Key via emergentintegrations

Prompt structuré envoyé à Claude:
  - Résumé des 5 premières pages crawlées
  - Contexte des 8 critères GEO
  - Demande de scoring 0-10 par critère
  - Génération de 10+ recommandations

Format de réponse: JSON structuré validé
```

### Phase 3: Génération de rapport (30% du temps)
```
Agrégation des scores
↓
Création des recommandations priorisées
↓
Génération PDF (ReportLab)
↓
Stockage MongoDB
```

---

## Les 8 critères GEO évalués

### 1. **Structure & Formatage** (0-10)
**Ce qui est évalué:**
- Hiérarchie HTML correcte (H1 → H2 → H3)
- Utilisation sémantique des balises
- Organisation logique du contenu
- Présence de listes, tableaux structurés

**Signaux analysés:**
- Nombre et qualité des headings
- Cohérence de la structure par page
- Respect des standards HTML5

**Exemple de score élevé (8-10):**
```html
<h1>Guide complet du courtage immobilier au Québec</h1>
<h2>Comment choisir un courtier</h2>
<h3>Critères de sélection</h3>
<ul>
  <li>Expérience vérifiable</li>
  <li>Zone géographique couverte</li>
</ul>
```

---

### 2. **Densité d'Information** (0-10)
**Ce qui est évalué:**
- Profondeur du contenu (>500 mots/page)
- Exhaustivité des sujets traités
- Ratio information/fluff
- Présence de données factuelles

**Signaux analysés:**
- Nombre de mots par page
- Diversité du vocabulaire
- Présence de statistiques, dates, chiffres

**Exemple de haute densité:**
```
"En 2024, le marché immobilier québécois a enregistré 
127 000 transactions, soit une hausse de 8% vs 2023. 
Le prix médian à Montréal atteint 542 000 $..."
```

---

### 3. **Lisibilité Machine/SEO** (0-10)
**Ce qui est évalué:**
- Meta descriptions (<160 caractères)
- JSON-LD structuré (Organization, FAQPage, etc.)
- Balises Open Graph
- URLs sémantiques
- Attributs alt sur images

**Signaux analysés:**
- Présence de meta description
- Validation JSON-LD
- Richesse du balisage sémantique

**Exemple de JSON-LD optimal:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "Qu'est-ce qu'un courtier immobilier?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Un courtier immobilier est un professionnel..."
    }
  }]
}
```

---

### 4. **E-E-A-T (Expertise, Experience, Authoritativeness, Trust)** (0-10)
**Ce qui est évalué:**
- Signatures d'auteurs avec bio
- Références et sources citées
- Preuves d'expertise (certifications, années d'expérience)
- Mentions légales et transparence

**Signaux analysés:**
- Présence de pages "À propos", "Équipe"
- Citations de sources externes fiables
- Témoignages clients
- Coordonnées complètes

**Exemple de fort E-E-A-T:**
```
"Par Marie Tremblay, courtière agréée depuis 1998,
membre de l'OACIQ (#A1234). Sources: Statistiques
Canada (2024), Centris."
```

---

### 5. **Contenu Éducatif** (0-10)
**Ce qui est évalué:**
- Guides pratiques et tutoriels
- FAQ détaillées
- Glossaires de termes
- Contenu "Comment faire"
- Exemples concrets

**Signaux analysés:**
- Pages de type "Guide", "FAQ", "Glossaire"
- Structure question-réponse
- Schémas explicatifs

**Exemple de contenu éducatif fort:**
```
FAQ: "Comment calculer l'hypothèque idéale?"
1. Déterminez votre mise de fonds (min 5%)
2. Calculez votre ratio d'endettement (<40%)
3. Exemple: Revenu 80k$ → capacité ~400k$
```

---

### 6. **Organisation Thématique** (0-10)
**Ce qui est évalué:**
- Architecture en silos thématiques
- Maillage interne cohérent
- Pages piliers + pages de support
- Navigation intuitive

**Signaux analysés:**
- Clustering des URLs par thème
- Nombre de liens internes
- Profondeur de navigation

**Exemple de bonne organisation:**
```
/courtage/
  /courtage/residentiel/
  /courtage/commercial/
  /courtage/guide-achat/
  /courtage/guide-vente/
```

---

### 7. **Optimisation IA (ChatGPT, Perplexity, AI Overviews)** (0-10)
**Ce qui est évalué:**
- Réponses rapides (40-60 mots)
- Définitions claires au début
- Format conversationnel
- Citations inline
- Contenu scannable

**Signaux analysés:**
- Paragraphes courts (<150 mots)
- Présence de définitions
- Format liste/bullet points
- Ton direct ("vous", "votre")

**Exemple de contenu optimisé IA:**
```
Qu'est-ce qu'une mise de fonds?

La mise de fonds est le montant que vous payez 
immédiatement lors de l'achat d'une propriété. 
Au Québec, elle représente minimum 5% du prix 
pour une première propriété. Exemple: Maison 
à 300 000 $ → mise de fonds minimale de 15 000 $.
```

---

### 8. **Visibilité Actuelle** (0-10)
**Ce qui est évalué:**
- Autorité perçue du domaine
- Fraîcheur du contenu (dates récentes)
- Signaux de ranking (HTTPS, vitesse)
- Présence sociale
- Backlinks (inféré)

**Signaux analysés:**
- Dates dans le contenu
- Mentions d'actualités récentes
- Sécurité (HTTPS)
- Volume de contenu publié

---

## Calcul du Score Global

```python
# Score global = moyenne arithmétique simple
global_score = (
    structure + 
    infoDensity + 
    readability + 
    eeat + 
    educational + 
    thematic + 
    aiOptimization + 
    visibility
) / 8

# Arrondi à 1 décimale
# Exemple: (7.5 + 5.3 + 6.8 + 6.2 + 4.5 + 5.7 + 3.8 + 6.0) / 8 = 5.7
```

### Interprétation des scores:
- **8.0 - 10.0**: Excellent - Site hautement optimisé pour IA
- **6.0 - 7.9**: Bon - Solide avec opportunités d'amélioration
- **4.0 - 5.9**: Moyen - Potentiel significatif d'optimisation
- **2.0 - 3.9**: Faible - Travail important requis
- **0.0 - 1.9**: Très faible - Refonte nécessaire

---

## Génération des recommandations

Claude génère automatiquement 10-15 recommandations basées sur l'analyse. Chaque recommandation inclut:

### Structure d'une recommandation:
```json
{
  "title": "Ajouter des FAQ structurées",
  "criterion": "educational",
  "impact": "high",      // high, medium, low
  "effort": "medium",    // high, medium, low
  "priority": 1,         // 1-10 (1 = plus prioritaire)
  "description": "Créez une section FAQ avec 15-20 questions...",
  "example": "JSON-LD FAQPage avec Question/Answer structuré"
}
```

### Priorisation automatique:
```
Priority Score = (Impact × 3) + (10 - Effort × 2)

Impact High + Effort Low = Priorité 1 (Quick Win)
Impact High + Effort High = Priorité 5 (Strategic)
Impact Low + Effort Low = Priorité 7 (Nice to have)
```

---

## Avantages de cette approche

✅ **Objectivité**: Analyse basée sur des signaux mesurables  
✅ **Intelligence contextuelle**: Claude comprend le contexte métier  
✅ **Reproductibilité**: Mêmes critères appliqués à tous les sites  
✅ **Actionnable**: Recommandations concrètes avec exemples  
✅ **Évolutif**: Prompt ajustable selon nouvelles tendances IA  

---

## Limitations actuelles

⚠️ **Volume de crawl**: Limité à 50 pages pour MVP (configurable)  
⚠️ **Pas d'accès aux analytics**: Pas de données de trafic réelles  
⚠️ **Pas de test en live**: Pas de requêtes réelles à ChatGPT/Perplexity  
⚠️ **JavaScript dynamique**: Crawl HTML statique uniquement  

---

## Améliorations futures possibles

1. **Crawl JavaScript**: Utiliser Playwright pour sites React/Vue
2. **API ChatGPT/Perplexity**: Tester visibilité réelle
3. **Suivi temporel**: Comparer scores sur plusieurs mois
4. **Benchmarking**: Comparer vs concurrents directs
5. **A/B Testing**: Mesurer impact des optimisations

---

*Dernière mise à jour: Novembre 2025*
*Modèle IA: Claude Sonnet 4 (Anthropic)*
