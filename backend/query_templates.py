"""
TEMPLATES DE REQUÊTES PAR INDUSTRIE
100% adaptatif selon l'industrie détectée
"""

# Templates de requêtes par type d'industrie
QUERY_TEMPLATES = {
    'financial_services': {
        'informational': [
            "meilleur {offering} {location}",
            "comment choisir {offering}",
            "guide {offering} {location}",
            "{offering} pour {segment}",
            "comparatif {offering} {location}",
            "prix {offering} {location}",
            "{offering} professionnel {location}",
            "différence entre {offering1} et {offering2}",
            "avantages {offering}",
            "{offering} entreprise vs particulier"
        ],
        'commercial': [
            "obtenir {offering} {location}",
            "soumission {offering} {location}",
            "devis {offering} en ligne",
            "demande {offering} rapide",
            "contact {offering} {location}",
            "{offering} tarif {location}",
            "rendez-vous {offering} {location}"
        ],
        'problem_based': [
            "comment {problem}",
            "{problem} solution",
            "éviter {problem}",
            "{problem} {location}",
            "protéger contre {problem}"
        ]
    },
    
    'saas': {
        'informational': [
            "meilleur logiciel {offering}",
            "{offering} logiciel comparatif",
            "outil {offering} entreprise",
            "{offering} plateforme",
            "alternative à {competitor}",
            "{offering} pour {use_case}",
            "{offering} prix",
            "comparatif {offering}",
            "guide {offering} logiciel",
            "{offering} features"
        ],
        'commercial': [
            "essai gratuit {offering}",
            "démo {offering} logiciel",
            "{offering} pricing",
            "acheter {offering}",
            "inscription {offering}",
            "{offering} abonnement"
        ],
        'problem_based': [
            "comment {problem} avec logiciel",
            "automatiser {problem}",
            "{problem} solution logiciel",
            "gérer {problem} en ligne",
            "résoudre {problem} automatiquement"
        ]
    },
    
    'ecommerce': {
        'informational': [
            "meilleur {offering}",
            "{offering} avis",
            "comparatif {offering}",
            "guide achat {offering}",
            "{offering} pour {use_case}",
            "où acheter {offering}",
            "{offering} qualité prix",
            "top {offering}",
            "{offering} pas cher",
            "{offering} haut de gamme"
        ],
        'commercial': [
            "acheter {offering} en ligne",
            "{offering} livraison rapide",
            "{offering} livraison gratuite",
            "commander {offering}",
            "promo {offering}",
            "{offering} solde",
            "{offering} {location}"
        ],
        'problem_based': [
            "trouver {offering} pour {problem}",
            "{offering} résoudre {problem}",
            "{problem} quel {offering}"
        ]
    },
    
    'construction': {
        'informational': [
            "meilleur {offering} {location}",
            "{offering} professionnel {location}",
            "prix {offering} {location}",
            "guide {offering}",
            "{offering} pour {segment}",
            "comparatif {offering} {location}",
            "{offering} entreprise {location}",
            "comment choisir {offering}"
        ],
        'commercial': [
            "soumission {offering} {location}",
            "devis {offering} gratuit",
            "{offering} estimation prix",
            "contact {offering} {location}",
            "{offering} urgence {location}",
            "rendez-vous {offering}"
        ],
        'problem_based': [
            "{problem} {location}",
            "solution {problem}",
            "réparer {problem} {location}",
            "comment {problem}"
        ]
    },
    
    'professional_services': {
        'informational': [
            "meilleur {offering} {location}",
            "{offering} professionnel {location}",
            "guide {offering}",
            "{offering} entreprise",
            "comparatif {offering}",
            "prix {offering} {location}",
            "{offering} pour {segment}",
            "comment choisir {offering}"
        ],
        'commercial': [
            "consultation {offering} {location}",
            "rendez-vous {offering}",
            "devis {offering} gratuit",
            "contact {offering} {location}",
            "{offering} tarif {location}"
        ],
        'problem_based': [
            "{problem} solution",
            "comment {problem}",
            "{problem} aide professionnelle",
            "résoudre {problem} {location}"
        ]
    },
    
    'healthcare': {
        'informational': [
            "meilleur {offering} {location}",
            "{offering} près de moi",
            "{offering} {location}",
            "guide {offering}",
            "{offering} spécialiste {location}",
            "comparatif {offering} {location}"
        ],
        'commercial': [
            "rendez-vous {offering} {location}",
            "consultation {offering}",
            "{offering} urgent {location}",
            "{offering} sans rendez-vous",
            "prendre rendez-vous {offering}"
        ],
        'problem_based': [
            "traiter {problem}",
            "{problem} solution",
            "{problem} {location}",
            "soigner {problem}"
        ]
    },
    
    'hospitality': {
        'informational': [
            "meilleur {offering} {location}",
            "{offering} près de moi",
            "top {offering} {location}",
            "{offering} avis {location}",
            "guide {offering} {location}",
            "{offering} recommandé {location}"
        ],
        'commercial': [
            "réservation {offering} {location}",
            "{offering} disponibilité",
            "réserver {offering} {location}",
            "{offering} tarif {location}",
            "{offering} promo {location}",
            "{offering} pas cher {location}"
        ],
        'problem_based': [
            "{offering} pour {occasion}",
            "{offering} {style}",
            "trouver {offering} {location}"
        ]
    },
    
    'real_estate': {
        'informational': [
            "meilleur {offering} {location}",
            "{offering} professionnel {location}",
            "guide {offering}",
            "{offering} prix {location}",
            "comment choisir {offering}",
            "{offering} avis {location}"
        ],
        'commercial': [
            "{offering} {location}",
            "contacter {offering}",
            "rendez-vous {offering} {location}",
            "{offering} évaluation gratuite",
            "{offering} consultation"
        ],
        'problem_based': [
            "vendre maison rapidement {location}",
            "acheter première maison {location}",
            "investir immobilier {location}",
            "trouver {offering} {location}"
        ]
    },
    
    'education': {
        'informational': [
            "meilleur {offering} {location}",
            "{offering} formation {location}",
            "guide {offering}",
            "programme {offering}",
            "{offering} diplôme",
            "comparatif {offering} {location}"
        ],
        'commercial': [
            "inscription {offering} {location}",
            "{offering} prix {location}",
            "demande information {offering}",
            "{offering} en ligne",
            "formation {offering}"
        ],
        'problem_based': [
            "apprendre {offering}",
            "se former à {offering}",
            "comment {offering}"
        ]
    },
    
    'manufacturing': {
        'informational': [
            "fabricant {offering} {location}",
            "meilleur {offering} {location}",
            "{offering} qualité",
            "producteur {offering}",
            "{offering} certification",
            "{offering} made in {location}"
        ],
        'commercial': [
            "acheter {offering}",
            "{offering} prix",
            "devis {offering}",
            "commande {offering}",
            "distributeur {offering} {location}"
        ],
        'problem_based': [
            "{offering} personnalisé",
            "{offering} sur mesure",
            "fabriquer {offering}"
        ]
    },
    
    'generic': {
        'informational': [
            "meilleur {offering} {location}",
            "{offering} {location}",
            "guide {offering}",
            "comment choisir {offering}",
            "comparatif {offering}",
            "{offering} prix",
            "{offering} professionnel"
        ],
        'commercial': [
            "obtenir {offering}",
            "demande {offering}",
            "contact {offering} {location}",
            "{offering} devis",
            "{offering} tarif"
        ],
        'problem_based': [
            "comment {problem}",
            "{problem} solution",
            "résoudre {problem}"
        ]
    }
}

def get_templates_for_industry(industry: str) -> Dict[str, List[str]]:
    """
    Retourner les templates appropriés pour une industrie
    
    Args:
        industry: Nom de l'industrie
    
    Returns:
        Dictionnaire de templates {category: [templates]}
    """
    
    # Mapping des industries vers les templates
    industry_mapping = {
        'financial_services': 'financial_services',
        'insurance': 'financial_services',
        'saas': 'saas',
        'software': 'saas',
        'technology': 'saas',
        'ecommerce': 'ecommerce',
        'retail': 'ecommerce',
        'construction': 'construction',
        'renovation': 'construction',
        'professional_services': 'professional_services',
        'consulting': 'professional_services',
        'legal': 'professional_services',
        'accounting': 'professional_services',
        'healthcare': 'healthcare',
        'medical': 'healthcare',
        'hospitality': 'hospitality',
        'restaurant': 'hospitality',
        'hotel': 'hospitality',
        'real_estate': 'real_estate',
        'immobilier': 'real_estate',
        'education': 'education',
        'training': 'education',
        'manufacturing': 'manufacturing',
        'production': 'manufacturing'
    }
    
    # Trouver le bon template
    template_key = industry_mapping.get(industry, 'generic')
    
    return QUERY_TEMPLATES.get(template_key, QUERY_TEMPLATES['generic'])
