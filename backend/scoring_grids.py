"""Grilles d'évaluation détaillées pour chaque critère GEO"""

SCORING_GRIDS = {
    "structure": {
        "name": "Structure & Formatage",
        "weight": 1.0,
        "elements_to_check": [
            "Présence de réponse directe dans les 40-60 premiers mots",
            "Sections TL;DR ou 'En Bref' au début des pages",
            "Hiérarchie H1 > H2 > H3 cohérente et descriptive",
            "Listes à puces pour information factuelle",
            "Tableaux comparatifs pour données complexes",
            "'Citation boxes' ou blocs extractibles",
            "Formatage scannable (pas de longs paragraphes)"
        ],
        "scoring_rules": {
            "9-10": "Excellence: Réponse directe systématique, TL;DR partout, structure impeccable, tableaux et listes",
            "7-8": "Très bon: Bonne structure générale, quelques TL;DR, hiérarchie correcte",
            "5-6": "Moyen: Structure acceptable mais pas optimisée, manque TL;DR, peu de listes",
            "3-4": "Insuffisant: Structure faible, pas de réponse directe, paragraphes longs",
            "0-2": "Critique: Aucune structure GEO, contenu purement marketing non-structuré"
        }
    },
    "infoDensity": {
        "name": "Densité d'Information",
        "weight": 1.2,
        "elements_to_check": [
            "Statistiques présentes (objectif: 1 stat. tous les 150-200 mots)",
            "Données chiffrées et mesurables",
            "Citations de sources autoritaires (études, instituts)",
            "Recherches propriétaires ou analyses originales",
            "Exemples concrets avec chiffres",
            "Profondeur du contenu (>1500 mots pour guides)",
            "Ratio information factuelle vs contenu marketing"
        ],
        "scoring_rules": {
            "9-10": "Excellence: Statistiques abondantes, données propriétaires, sources citées systématiquement",
            "7-8": "Très bon: Bonnes statistiques, quelques données originales, sources présentes",
            "5-6": "Moyen: Quelques statistiques, manque de données originales",
            "3-4": "Insuffisant: Très peu de données chiffrées, pas de sources",
            "0-2": "Critique: Aucune statistique, aucune donnée factuelle, contenu marketing pur"
        }
    },
    "readability": {
        "name": "Lisibilité Machine/SEO",
        "weight": 1.0,
        "elements_to_check": [
            "Meta descriptions factuelles (<120 caractères)",
            "Schema.org Organization implémenté",
            "Schema.org LocalBusiness pour succursales",
            "Schema.org FAQPage pour FAQ",
            "Schema.org Article pour contenu éditorial",
            "JSON-LD structuré et valide",
            "Balisage sémantique (Open Graph, Twitter Cards)",
            "URLs descriptives et propres"
        ],
        "scoring_rules": {
            "9-10": "Excellence: Schema complet, JSON-LD partout, meta factuelles, balisage impeccable",
            "7-8": "Très bon: Schema principal OK, quelques JSON-LD, bonnes meta",
            "5-6": "Moyen: Schema basique, meta acceptables mais pas optimales",
            "3-4": "Insuffisant: Schema incomplet, meta marketing, balisage faible",
            "0-2": "Critique: Aucun schema, meta inutiles, pas de structured data"
        }
    },
    "eeat": {
        "name": "E-E-A-T (Expertise, Experience, Authoritativeness, Trust)",
        "weight": 1.1,
        "elements_to_check": [
            "Auteurs identifiés avec nom, photo, bio",
            "Certifications et qualifications affichées",
            "Page 'À propos' détaillée avec historique",
            "Mentions médias et presse récentes",
            "Témoignages clients structurés",
            "Preuves d'expertise (awards, reconnaissances)",
            "Transparence (coordonnées complètes, mentions légales)",
            "Publications externes et thought leadership"
        ],
        "scoring_rules": {
            "9-10": "Excellence: Auteurs experts identifiés, certifications affichées, forte autorité médias",
            "7-8": "Très bon: Bons auteurs, quelques certifications, présence médias",
            "5-6": "Moyen: Organisation crédible mais auteurs anonymes, peu de preuves",
            "3-4": "Insuffisant: Faible E-E-A-T, pas d'auteurs, peu de preuves d'expertise",
            "0-2": "Critique: Aucun E-E-A-T, contenu anonyme, aucune preuve d'autorité"
        }
    },
    "educational": {
        "name": "Contenu Éducatif",
        "weight": 1.3,
        "elements_to_check": [
            "Guides complets (>1500 mots)",
            "FAQ détaillées et structurées",
            "Glossaires de termes techniques",
            "Tutoriels et 'Comment faire'",
            "Études de cas avec résultats mesurables",
            "Contenu pédagogique objectif (non-promotionnel)",
            "Ressources téléchargeables (PDF, infographies)",
            "Calculateurs et outils interactifs"
        ],
        "scoring_rules": {
            "9-10": "Excellence: 50+ guides éducatifs, FAQ riches, glossaires, outils interactifs",
            "7-8": "Très bon: 20-50 guides, bonnes FAQ, contenu pédagogique solide",
            "5-6": "Moyen: 10-20 articles éducatifs, quelques FAQ basiques",
            "3-4": "Insuffisant: <10 articles éducatifs, contenu superficiel",
            "0-2": "Critique: Aucun contenu éducatif, 100% marketing/vente"
        }
    },
    "thematic": {
        "name": "Organisation Thématique",
        "weight": 0.9,
        "elements_to_check": [
            "Architecture en silos thématiques",
            "Pages piliers (hub) bien définies",
            "Articles satellites liés au pilier",
            "Maillage interne cohérent (5-10 liens/article)",
            "Breadcrumbs avec schema markup",
            "Clustering de contenu par thème",
            "Navigation intuitive par sujet",
            "Profondeur de navigation optimale (<3 clics)"
        ],
        "scoring_rules": {
            "9-10": "Excellence: 5+ hubs thématiques avec 15-20 satellites chacun, maillage fort",
            "7-8": "Très bon: 3-5 hubs avec satellites, bon maillage interne",
            "5-6": "Moyen: Début de clustering, maillage faible, structure peu claire",
            "3-4": "Insuffisant: Pas de silos, liens internes rares, navigation confuse",
            "0-2": "Critique: Aucune organisation thématique, contenu en silo isolé"
        }
    },
    "aiOptimization": {
        "name": "Optimisation IA",
        "weight": 1.2,
        "elements_to_check": [
            "Format conversationnel et direct",
            "Définitions claires au début",
            "Réponses rapides (40-60 mots)",
            "Paragraphes courts (<150 mots)",
            "Ton informatif et objectif",
            "Citations inline facilement extractibles",
            "Adaptation ChatGPT/Perplexity/Claude",
            "Contenu scannable pour extraction IA"
        ],
        "scoring_rules": {
            "9-10": "Excellence: Format optimal IA, réponses rapides partout, contenu extractible",
            "7-8": "Très bon: Bon format, quelques réponses rapides, ton adapté",
            "5-6": "Moyen: Format acceptable mais pas optimisé, manque réponses directes",
            "3-4": "Insuffisant: Format peu adapté IA, ton marketing, contenu non-extractible",
            "0-2": "Critique: Aucune optimisation IA, format anti-IA (marketing lourd)"
        }
    },
    "visibility": {
        "name": "Visibilité Actuelle",
        "weight": 1.0,
        "elements_to_check": [
            "Présence dans réponses ChatGPT/Perplexity",
            "Citations dans Google AI Overviews",
            "Autorité perçue du domaine",
            "Fraîcheur du contenu (dates récentes)",
            "Signaux de ranking (HTTPS, vitesse, mobile)",
            "Backlinks de qualité",
            "Mentions sur réseaux sociaux",
            "Volume de contenu indexable"
        ],
        "scoring_rules": {
            "9-10": "Excellence: Très visible dans toutes les IA, citations fréquentes",
            "7-8": "Très bon: Visible dans plusieurs IA, quelques citations",
            "5-6": "Moyen: Visibilité occasionnelle, rares citations",
            "3-4": "Insuffisant: Très faible visibilité, presque aucune citation",
            "0-2": "Critique: Invisible dans toutes les IA, aucune citation"
        }
    }
}

def get_scoring_prompt() -> str:
    """Génère le prompt détaillé avec grilles d'évaluation pour Claude"""
    prompt_parts = [
        "Vous êtes un expert GEO (Generative Engine Optimization) de niveau mondial.",
        "Votre rôle est d'analyser rigoureusement un site web selon 8 critères précis.",
        "",
        "IMPORTANT: Utilisez les grilles d'évaluation ci-dessous pour scorer chaque critère.",
        "Vous devez fournir:",
        "1. Un score 0-10 JUSTIFIÉ pour chaque critère",
        "2. Des OBSERVATIONS SPÉCIFIQUES sur le contenu analysé",
        "3. Des EXEMPLES CONCRETS tirés du site",
        "4. Des PROBLÈMES IDENTIFIÉS précis",
        "5. Des RECOMMANDATIONS ACTIONNABLES",
        "",
        "="*80,
        "GRILLES D'ÉVALUATION DÉTAILLÉES",
        "="*80,
        ""
    ]
    
    for criterion_key, criterion_data in SCORING_GRIDS.items():
        prompt_parts.extend([
            f"\n### {criterion_data['name'].upper()} (poids: {criterion_data['weight']})",
            "",
            "Éléments à vérifier:"
        ])
        for element in criterion_data['elements_to_check']:
            prompt_parts.append(f"  ✓ {element}")
        
        prompt_parts.extend([
            "",
            "Grille de notation:"
        ])
        for score_range, description in criterion_data['scoring_rules'].items():
            prompt_parts.append(f"  {score_range}: {description}")
    
    return "\n".join(prompt_parts)
