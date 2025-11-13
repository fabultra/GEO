"""
MODULE DE GÉNÉRATION INTELLIGENTE DE REQUÊTES V2
Génère 30 requêtes contextuelles et pertinentes basées sur l'analyse réelle du site
"""
import logging
import re
from typing import List, Dict, Any
from collections import Counter

logger = logging.getLogger(__name__)

class IntelligentQueryGenerator:
    """Génère des requêtes contextuelles basées sur le contenu réel du site"""
    
    def __init__(self):
        self.queries = []
        self.context = {}
    
    def generate_contextual_queries(self, crawl_data: Dict[str, Any], num_queries: int = 30) -> List[str]:
        """
        Génère des requêtes PERTINENTES basées sur le contexte réel
        
        Args:
            crawl_data: Données du crawl du site
            num_queries: Nombre de requêtes à générer (default: 30)
        
        Returns:
            Liste de 30 requêtes contextuelles et pertinentes
        """
        try:
            # 1. Analyser le contexte du site
            self.context = self._analyze_site_context(crawl_data)
            
            queries = []
            
            # 2. Requêtes de marque (5 requêtes)
            queries.extend(self._generate_brand_queries())
            
            # 3. Requêtes par service (8-10 requêtes)
            queries.extend(self._generate_service_queries())
            
            # 4. Requêtes long-tail spécifiques (8 requêtes)
            queries.extend(self._generate_industry_specific_queries())
            
            # 5. Requêtes de considération (5 requêtes)
            queries.extend(self._generate_consideration_queries())
            
            # 6. Requêtes d'intention (4 requêtes)
            queries.extend(self._generate_intent_queries())
            
            # Nettoyer et dédupliquer
            queries = list(dict.fromkeys(queries))  # Remove duplicates
            queries = [q for q in queries if q and len(q) > 10]  # Filter short queries
            
            logger.info(f"Generated {len(queries)} contextual queries")
            
            return queries[:num_queries]
            
        except Exception as e:
            logger.error(f"Error generating queries: {str(e)}")
            # Fallback to basic queries
            return self._generate_fallback_queries(crawl_data)
    
    def _analyze_site_context(self, crawl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extraire le contexte complet du site"""
        
        context = {
            'company_name': '',
            'industry': '',
            'services': [],
            'locations': [],
            'keywords': [],
            'competitors': []
        }
        
        pages = crawl_data.get('pages', [])
        if not pages:
            return context
        
        # Extraire le nom de l'entreprise
        first_page = pages[0]
        title = first_page.get('title', '')
        
        # Nom d'entreprise = premier mot du title avant | ou -
        if '|' in title:
            context['company_name'] = title.split('|')[0].strip()
        elif '-' in title:
            context['company_name'] = title.split('-')[0].strip()
        else:
            context['company_name'] = title.split()[0] if title else ''
        
        # Identifier l'industrie
        context['industry'] = self._identify_industry(crawl_data)
        
        # Extraire les services
        context['services'] = self._extract_services(crawl_data)
        
        # Extraire les localisations
        context['locations'] = self._extract_locations(crawl_data)
        
        # Extraire les mots-clés principaux
        context['keywords'] = self._extract_keywords(crawl_data)
        
        logger.info(f"Context analyzed: {context['company_name']} - {context['industry']}")
        
        return context
    
    def _identify_industry(self, crawl_data: Dict[str, Any]) -> str:
        """Identifier l'industrie du site"""
        
        # Combiner tout le texte
        all_text = ""
        for page in crawl_data.get('pages', []):
            all_text += " " + page.get('title', '')
            all_text += " " + " ".join(page.get('paragraphs', []))
        
        all_text = all_text.lower()
        
        # Patterns par industrie
        industry_patterns = {
            'assurance': ['assurance', 'courtier', 'police', 'prime', 'sinistre', 'couverture', 'indemnité'],
            'immobilier': ['immobilier', 'propriété', 'maison', 'condo', 'hypothèque', 'achat', 'vente'],
            'finance': ['finance', 'placement', 'investissement', 'retraite', 'épargne', 'planification'],
            'santé': ['santé', 'médical', 'clinique', 'docteur', 'patient', 'traitement'],
            'technologie': ['logiciel', 'application', 'tech', 'digital', 'développement', 'web'],
            'juridique': ['avocat', 'droit', 'juridique', 'légal', 'litige', 'contrat'],
            'restauration': ['restaurant', 'menu', 'cuisine', 'chef', 'réservation', 'gastronomie'],
            'éducation': ['école', 'cours', 'formation', 'apprentissage', 'étudiant', 'enseignement']
        }
        
        # Compter les occurrences
        scores = {}
        for industry, keywords in industry_patterns.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            scores[industry] = score
        
        # Retourner l'industrie avec le score le plus élevé
        if scores:
            industry = max(scores, key=scores.get)
            if scores[industry] > 0:
                return industry
        
        return 'default'
    
    def _extract_services(self, crawl_data: Dict[str, Any]) -> List[str]:
        """Extraire les services offerts"""
        
        services = []
        
        # Patterns de services par industrie
        if self.context.get('industry') == 'assurance':
            service_keywords = [
                'assurance habitation', 'assurance auto', 'assurance vie',
                'assurance entreprise', 'assurance responsabilité', 'assurance invalidité',
                'planification financière', 'planification retraite', 'assurance groupe'
            ]
        elif self.context.get('industry') == 'immobilier':
            service_keywords = [
                'achat propriété', 'vente propriété', 'évaluation',
                'courtage immobilier', 'gestion immobilière'
            ]
        else:
            service_keywords = []
        
        # Chercher dans le contenu
        all_text = ""
        for page in crawl_data.get('pages', []):
            all_text += " " + " ".join(page.get('paragraphs', []))
        
        all_text = all_text.lower()
        
        for service in service_keywords:
            if service in all_text:
                services.append(service)
        
        # Si aucun service trouvé, utiliser l'industrie comme service
        if not services and self.context.get('industry'):
            services.append(self.context['industry'])
        
        return services[:5]  # Max 5 services
    
    def _extract_locations(self, crawl_data: Dict[str, Any]) -> List[str]:
        """Extraire les localisations mentionnées"""
        
        locations = []
        
        # Villes du Québec communes
        quebec_cities = [
            'Montréal', 'Québec', 'Laval', 'Gatineau', 'Longueuil',
            'Sherbrooke', 'Saguenay', 'Trois-Rivières', 'Terrebonne', 'Brossard'
        ]
        
        all_text = ""
        for page in crawl_data.get('pages', []):
            all_text += " " + " ".join(page.get('paragraphs', []))
        
        for city in quebec_cities:
            if city.lower() in all_text.lower():
                locations.append(city)
        
        # Toujours ajouter "Québec" comme région
        if 'Québec' not in locations:
            locations.append('Québec')
        
        return locations[:3]  # Max 3 localisations
    
    def _extract_keywords(self, crawl_data: Dict[str, Any]) -> List[str]:
        """Extraire les mots-clés principaux"""
        
        # Combiner tout le texte
        all_text = ""
        for page in crawl_data.get('pages', []):
            all_text += " " + " ".join(page.get('paragraphs', []))
        
        # Tokenize et compter
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]{4,}\b', all_text.lower())
        
        # Mots à exclure
        stop_words = set(['dans', 'pour', 'avec', 'vous', 'nous', 'votre', 'notre', 'plus', 'tout', 'tous', 'toute', 'cette', 'sont', 'être', 'avoir', 'faire', 'leur', 'leurs'])
        
        # Filtrer et compter
        filtered_words = [w for w in words if w not in stop_words]
        word_freq = Counter(filtered_words)
        
        # Top 10 mots
        top_keywords = [word for word, count in word_freq.most_common(10)]
        
        return top_keywords
    
    def _generate_brand_queries(self) -> List[str]:
        """Générer 5 requêtes de marque"""
        
        company = self.context.get('company_name', 'entreprise')
        location = self.context.get('locations', ['Québec'])[0]
        
        return [
            f"{company} avis",
            f"{company} {location}",
            f"pourquoi choisir {company}",
            f"{company} vs concurrent",
            f"avis clients {company}"
        ]
    
    def _generate_service_queries(self) -> List[str]:
        """Générer 8-10 requêtes par service"""
        
        services = self.context.get('services', [])
        location = self.context.get('locations', ['Québec'])[0] if self.context.get('locations') else 'Québec'
        company = self.context.get('company_name', 'entreprise')
        
        queries = []
        
        # Si on a des services, les utiliser
        if services:
            for service in services[:2]:  # Top 2 services
                queries.extend([
                    f"meilleur {service} {location}",
                    f"comment choisir {service}",
                    f"{service} prix {location}",
                    f"comparatif {service} {location}",
                    f"guide {service} 2025"
                ])
        else:
            # Sinon, requêtes génériques avec le nom de l'entreprise
            queries.extend([
                f"services {company}",
                f"comment choisir {company}",
                f"{company} prix {location}",
                f"comparatif {company}",
                f"guide {company} 2025"
            ])
        
        return queries[:10]
    
    def _generate_industry_specific_queries(self) -> List[str]:
        """Générer 8 requêtes long-tail spécifiques à l'industrie"""
        
        industry = self.context.get('industry', 'default')
        location = self.context.get('locations', ['Québec'])[0]
        company = self.context.get('company_name', '')
        
        industry_queries = {
            'assurance': [
                f"courtier assurance indépendant {location}",
                f"économiser assurance habitation {location}",
                f"réclamation assurance rapide {location}",
                f"assurance entreprise PME {location}",
                f"planification financière retraite {location}",
                "assurance vie temporaire vs permanente",
                f"courtier assurance famille {location}",
                f"protection financière complète {location}"
            ],
            'immobilier': [
                f"courtier immobilier expérimenté {location}",
                f"vendre maison rapidement {location}",
                f"acheter première maison {location}",
                f"évaluation propriété gratuite {location}",
                f"frais courtier immobilier {location}",
                "inspection maison avant achat",
                f"offre d'achat conditions {location}",
                f"prix maison {location} 2025"
            ],
            'finance': [
                f"conseiller financier indépendant {location}",
                f"planification retraite {location}",
                f"placement REER CELI {location}",
                f"gestion patrimoine {location}",
                f"investissement immobilier {location}",
                f"stratégie fiscale {location}",
                f"planification succession {location}",
                f"conseils financiers gratuits {location}"
            ],
            'default': [
                f"meilleur service {industry} {location}",
                f"comment choisir {industry} {location}",
                f"prix {industry} {location}",
                f"comparatif {industry} {location}",
                f"guide {industry} débutant",
                f"{industry} professionnel {location}",
                f"avis {industry} {location}",
                f"{industry} entreprise {location}"
            ]
        }
        
        return industry_queries.get(industry, industry_queries['default'])[:8]
    
    def _generate_consideration_queries(self) -> List[str]:
        """Générer 5 requêtes de considération (milieu du funnel)"""
        
        services = self.context.get('services', [])
        service = services[0] if services else self.context.get('company_name', 'service')
        location = self.context.get('locations', ['Québec'])[0] if self.context.get('locations') else 'Québec'
        
        return [
            f"différence entre {service} options",
            f"avantages {service}",
            f"coût moyen {service} {location}",
            f"{service} pour entreprise",
            f"erreurs à éviter {service}"
        ]
    
    def _generate_intent_queries(self) -> List[str]:
        """Générer 4 requêtes d'intention (bottom funnel)"""
        
        service = self.context.get('services', ['service'])[0]
        location = self.context.get('locations', ['Québec'])[0]
        
        return [
            f"obtenir soumission {service} {location}",
            f"demande {service} en ligne",
            f"rendez-vous {service} {location}",
            f"contact {service} {location}"
        ]
    
    def _generate_fallback_queries(self, crawl_data: Dict[str, Any]) -> List[str]:
        """Requêtes de fallback si l'analyse échoue"""
        
        url = crawl_data.get('url', '')
        domain = url.split('//')[1].split('/')[0] if '//' in url else url
        company_name = domain.split('.')[0].upper()
        
        return [
            f"{company_name} avis",
            f"meilleurs services {company_name}",
            f"{company_name} Québec",
            f"comment choisir {company_name}",
            f"{company_name} prix",
            f"comparatif {company_name}",
            f"guide {company_name}",
            f"{company_name} vs concurrent",
            f"avis clients {company_name}",
            f"{company_name} Montréal",
            "meilleurs services Québec",
            "comment choisir service professionnel",
            "prix services Québec",
            "comparatif services Montréal",
            "guide services 2025",
            "services professionnels Québec",
            "avis services Montréal",
            "choisir professionnel Québec",
            "services entreprise Québec",
            "obtenir soumission Québec"
        ]


# Fonction principale compatible avec l'ancienne API
def generate_queries(crawl_data: Dict[str, Any], num_queries: int = 30) -> List[str]:
    """
    Fonction wrapper pour compatibilité avec l'ancien code
    
    Args:
        crawl_data: Données du crawl
        num_queries: Nombre de requêtes à générer
    
    Returns:
        Liste de requêtes contextuelles
    """
    generator = IntelligentQueryGenerator()
    return generator.generate_contextual_queries(crawl_data, num_queries)
