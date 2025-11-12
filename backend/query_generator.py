"""
Générateur de requêtes de test intelligentes basées sur l'industrie et le contenu du site
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

INDUSTRY_QUERIES = {
    "assurance": [
        "meilleurs courtiers assurance Québec",
        "comment choisir assurance habitation",
        "assurance auto Montréal prix",
        "courtier assurance entreprise Québec",
        "planification financière retraite",
        "assurance vie temporaire vs permanente",
        "comparatif assurance habitation Québec",
        "assurance locataire vs propriétaire",
        "quelle assurance choisir",
        "comment réduire prime assurance",
        "courtier assurance Montréal",
        "assurance habitation Québec guide",
        "assurance copropriété Montréal",
        "assurance groupe employés PME",
        "assurance responsabilité civile pro",
        "assurance vie maladies graves",
        "planification succession Québec",
        "assurance entreprise construction",
        "courtier indépendant vs captif",
        "assurance invalidité travailleur autonome"
    ],
    "immobilier": [
        "meilleurs courtiers immobiliers Québec",
        "comment vendre maison rapidement",
        "prix maison Montréal 2025",
        "acheter première maison Québec",
        "courtier immobilier frais",
        "évaluation propriété gratuite",
        "acheter vs louer Québec",
        "inspection maison avant achat",
        "offre d'achat conditions",
        "mise de fonds minimum première maison"
    ],
    "default": [
        "meilleurs {service} Québec",
        "comment choisir {service}",
        "{service} prix Montréal",
        "comparatif {service} Québec",
        "guide {service} débutant",
        "{service} professionnel vs autonome",
        "erreurs éviter {service}",
        "{service} en ligne vs présentiel",
        "combien coûte {service}",
        "avis {service} Québec"
    ]
}

def generate_test_queries(site_url: str, crawl_data: Dict[str, Any], industry: str = None) -> List[str]:
    """
    Génère des requêtes de test intelligentes basées sur:
    - L'industrie du site
    - Le contenu crawlé
    - Les mots-clés extraits
    
    Args:
        site_url: URL du site
        crawl_data: Données du crawl
        industry: Industrie (optionnel, sera déduit si non fourni)
    
    Returns:
        Liste de 20 requêtes de test
    """
    queries = []
    
    # Extraire des mots-clés du contenu
    keywords = extract_keywords_from_crawl(crawl_data)
    
    # Détecter l'industrie si non fournie
    if not industry:
        industry = detect_industry(crawl_data, keywords)
    
    # Récupérer les requêtes de base pour l'industrie
    if industry in INDUSTRY_QUERIES:
        queries.extend(INDUSTRY_QUERIES[industry][:15])
    else:
        # Utiliser les templates par défaut avec les keywords
        main_keyword = keywords[0] if keywords else "service"
        for template in INDUSTRY_QUERIES["default"][:10]:
            queries.append(template.replace("{service}", main_keyword))
    
    # Ajouter des requêtes basées sur le contenu spécifique du site
    content_queries = generate_content_based_queries(crawl_data, keywords)
    queries.extend(content_queries[:5])
    
    # Compléter à 20 requêtes si nécessaire
    while len(queries) < 20:
        if keywords:
            queries.append(f"guide {keywords[0]} Québec")
            if len(keywords) > 1:
                queries.append(f"{keywords[0]} vs {keywords[1]}")
        else:
            break
    
    return queries[:20]

def extract_keywords_from_crawl(crawl_data: Dict[str, Any]) -> List[str]:
    """Extrait les mots-clés principaux du contenu crawlé"""
    keywords = set()
    
    for page in crawl_data.get('pages', [])[:5]:
        # Extraire des H1 et H2
        for h1 in page.get('h1', []):
            words = h1.lower().split()
            keywords.update([w for w in words if len(w) > 4])
        
        for h2 in page.get('h2', [])[:3]:
            words = h2.lower().split()
            keywords.update([w for w in words if len(w) > 4])
    
    # Filtrer les mots communs
    stopwords = {'pour', 'avec', 'dans', 'vous', 'votre', 'notre', 'leurs', 'comment', 'pourquoi'}
    keywords = [k for k in keywords if k not in stopwords]
    
    return list(keywords)[:10]

def detect_industry(crawl_data: Dict[str, Any], keywords: List[str]) -> str:
    """Détecte l'industrie du site basé sur le contenu"""
    
    # Mots-clés par industrie
    industry_keywords = {
        "assurance": ["assurance", "courtier", "prime", "police", "sinistre", "couverture", "protection"],
        "immobilier": ["immobilier", "propriété", "maison", "condo", "vente", "achat", "hypothèque"],
        "finance": ["finance", "investissement", "épargne", "retraite", "planification", "patrimoine"],
        "santé": ["santé", "médical", "clinique", "soins", "traitement", "patient"],
        "technologie": ["technologie", "logiciel", "application", "digital", "numérique", "développement"],
        "consultation": ["consultation", "conseil", "expert", "stratégie", "accompagnement"]
    }
    
    # Compter les occurrences
    scores = {}
    content_text = " ".join(keywords).lower()
    
    for industry, terms in industry_keywords.items():
        score = sum(1 for term in terms if term in content_text)
        if score > 0:
            scores[industry] = score
    
    if scores:
        return max(scores, key=scores.get)
    
    return "default"

def generate_content_based_queries(crawl_data: Dict[str, Any], keywords: List[str]) -> List[str]:
    """Génère des requêtes basées sur le contenu spécifique du site"""
    queries = []
    
    # Extraire les titres de pages
    for page in crawl_data.get('pages', [])[:3]:
        title = page.get('title', '')
        if title and len(title) > 10:
            # Convertir le titre en question
            queries.append(f"avis {title}")
            queries.append(f"comment {title.lower()}")
    
    return queries[:5]
