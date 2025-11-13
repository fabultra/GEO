"""
MODULE DE GÉNÉRATION INTELLIGENTE DE REQUÊTES V2
Génère 100 requêtes dont 80% NON-BRANDED basées sur analyse sémantique profonde
100% ADAPTATIF à toute industrie

Utilise:
- semantic_analyzer.py pour comprendre le site
- query_templates.py pour les templates par industrie
"""
import logging
import random
from typing import List, Dict, Any
from semantic_analyzer import SemanticAnalyzer
from query_templates import get_templates_for_industry

logger = logging.getLogger(__name__)


class IntelligentQueryGeneratorV2:
    """Génère 100 requêtes contextuelles dont 80% non-branded"""
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self.semantic_results = {}
    
    def generate_intelligent_queries(self, crawl_data: Dict[str, Any], num_queries: int = 100) -> Dict[str, Any]:
        """
        Génère 100 requêtes intelligentes basées sur l'analyse sémantique
        
        Args:
            crawl_data: Données du crawl du site
            num_queries: Nombre de requêtes à générer (default: 100)
        
        Returns:
            {
                'queries': [...],
                'semantic_analysis': {...},
                'breakdown': {...}
            }
        """
        try:
            logger.info("🧠 Starting semantic analysis...")
            
            # 1. ANALYSE SÉMANTIQUE PROFONDE
            self.semantic_results = self.semantic_analyzer.analyze_site(crawl_data)
            
            industry = self.semantic_results.get('industry_classification', {}).get('primary_industry', 'generic')
            entities = self.semantic_results.get('entities', {})
            
            logger.info(f"✅ Industry detected: {industry}")
            logger.info(f"✅ Offerings found: {len(entities.get('offerings', []))}")
            
            # 2. OBTENIR LES TEMPLATES POUR L'INDUSTRIE
            templates = get_templates_for_industry(industry)
            
            # 3. GÉNÉRER LES REQUÊTES PAR CATÉGORIE
            queries = {
                'non_branded': [],
                'semi_branded': [],
                'branded': []
            }
            
            # 3.1 NON-BRANDED (80 requêtes)
            queries['non_branded'] = self._generate_non_branded_queries(entities, templates, industry)
            
            # 3.2 SEMI-BRANDED (15 requêtes)
            queries['semi_branded'] = self._generate_semi_branded_queries(entities)
            
            # 3.3 BRANDED (5 requêtes)
            queries['branded'] = self._generate_branded_queries(entities)
            
            # 4. ASSEMBLER ET NETTOYER
            final_queries = []
            final_queries.extend(queries['non_branded'][:80])
            final_queries.extend(queries['semi_branded'][:15])
            final_queries.extend(queries['branded'][:5])
            
            # Dédupliquer et nettoyer
            final_queries = self._clean_and_deduplicate(final_queries)
            
            # 5. COMPLÉTER SI NÉCESSAIRE
            if len(final_queries) < num_queries:
                logger.warning(f"Only {len(final_queries)} queries generated, filling with generic ones")
                final_queries.extend(self._generate_generic_queries(entities, num_queries - len(final_queries)))
            
            final_queries = final_queries[:num_queries]
            
            logger.info(f"✅ Generated {len(final_queries)} queries total")
            
            return {
                'queries': final_queries,
                'semantic_analysis': self.semantic_results,
                'breakdown': {
                    'non_branded': len([q for q in final_queries[:80]]),
                    'semi_branded': len([q for q in final_queries[80:95]]),
                    'branded': len([q for q in final_queries[95:100]]),
                    'total': len(final_queries)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating intelligent queries: {str(e)}")
            # Fallback to basic queries
            return self._generate_fallback_queries(crawl_data, num_queries)
    
    def _generate_non_branded_queries(self, entities: Dict[str, Any], templates: Dict[str, List[str]], industry: str) -> List[str]:
        """Générer 80 requêtes NON-BRANDED"""
        
        queries = []
        
        offerings = entities.get('offerings', [])
        locations = entities.get('locations', [])
        segments = entities.get('customer_segments', [])
        problems = entities.get('problems_solved', [])
        company_type = entities.get('company_info', {}).get('type', 'entreprise')
        
        # Extraire valeurs
        offering_names = [o.get('name', '') for o in offerings[:5]]
        location_names = [loc.get('city') if loc.get('city') else loc.get('region', 'Québec') for loc in locations[:3]]
        
        # Si pas de données, utiliser des valeurs par défaut
        if not offering_names:
            offering_names = [company_type, 'service', 'solution']
        if not location_names:
            location_names = ['Québec', 'Montréal']
        if not segments:
            segments = ['entreprise', 'particulier']
        if not problems:
            problems = ['optimiser', 'améliorer', 'simplifier']
        
        # 1. INFORMATIONAL QUERIES (40 requêtes)
        informational_templates = templates.get('informational', [])
        for template in informational_templates[:8]:
            for offering in offering_names[:3]:
                for location in location_names[:2]:
                    try:
                        query = template.format(
                            offering=offering,
                            location=location,
                            segment=segments[0] if segments else 'entreprise',
                            use_case='entreprise',
                            offering1=offering_names[0] if len(offering_names) > 0 else 'service',
                            offering2=offering_names[1] if len(offering_names) > 1 else 'solution',
                            competitor='alternative'
                        )
                        queries.append(query)
                    except Exception:
                        pass
        
        # 2. COMMERCIAL QUERIES (20 requêtes)
        commercial_templates = templates.get('commercial', [])
        for template in commercial_templates[:5]:
            for offering in offering_names[:2]:
                for location in location_names[:2]:
                    try:
                        query = template.format(
                            offering=offering,
                            location=location
                        )
                        queries.append(query)
                    except Exception:
                        pass
        
        # 3. PROBLEM-BASED QUERIES (20 requêtes)
        problem_templates = templates.get('problem_based', [])
        for template in problem_templates[:5]:
            for problem in problems[:2]:
                for location in location_names[:2]:
                    try:
                        query = template.format(
                            problem=problem,
                            location=location,
                            offering=offering_names[0] if offering_names else 'solution'
                        )
                        queries.append(query)
                    except Exception:
                        pass
        
        return queries[:80]
    
    def _generate_semi_branded_queries(self, entities: Dict[str, Any]) -> List[str]:
        """Générer 15 requêtes SEMI-BRANDED (type d'entreprise + localisation)"""
        
        queries = []
        
        company_type = entities.get('company_info', {}).get('type', 'entreprise')
        offerings = entities.get('offerings', [])
        locations = entities.get('locations', [])
        
        offering_names = [o.get('name', '') for o in offerings[:3]]
        location_names = [loc.get('city') if loc.get('city') else loc.get('region', 'Québec') for loc in locations[:3]]
        
        if not location_names:
            location_names = ['Québec', 'Montréal']
        
        # Patterns semi-branded
        for location in location_names:
            queries.append(f"meilleur {company_type} {location}")
            queries.append(f"{company_type} professionnel {location}")
            queries.append(f"{company_type} près de moi")
            
            for offering in offering_names[:2]:
                queries.append(f"{company_type} {offering} {location}")
                queries.append(f"trouver {company_type} {offering}")
        
        return queries[:15]
    
    def _generate_branded_queries(self, entities: Dict[str, Any]) -> List[str]:
        """Générer 5 requêtes BRANDED (nom de l'entreprise)"""
        
        company_name = entities.get('company_info', {}).get('name', 'entreprise')
        locations = entities.get('locations', [])
        location = locations[0].get('city') if locations and locations[0].get('city') else 'Québec'
        
        return [
            f"{company_name} avis",
            f"{company_name} {location}",
            f"pourquoi choisir {company_name}",
            f"{company_name} vs concurrent",
            f"avis clients {company_name}"
        ]
    
    def _generate_generic_queries(self, entities: Dict[str, Any], num: int) -> List[str]:
        """Générer des requêtes génériques de remplissage"""
        
        company_type = entities.get('company_info', {}).get('type', 'entreprise')
        locations = entities.get('locations', [])
        location = locations[0].get('city') if locations and locations[0].get('city') else 'Québec'
        
        generic = [
            f"meilleur {company_type} {location}",
            f"{company_type} prix {location}",
            f"guide {company_type}",
            f"comparatif {company_type} {location}",
            f"comment choisir {company_type}",
            f"{company_type} professionnel",
            f"{company_type} entreprise {location}",
            f"services {company_type}",
            f"{company_type} avis",
            f"obtenir {company_type}"
        ]
        
        return generic[:num]
    
    def _clean_and_deduplicate(self, queries: List[str]) -> List[str]:
        """Nettoyer et dédupliquer les requêtes"""
        
        cleaned = []
        seen = set()
        
        for query in queries:
            if not query:
                continue
            
            # Nettoyer
            query = query.strip().lower()
            query = ' '.join(query.split())  # Remove extra spaces
            
            # Valider
            if len(query) < 5 or len(query.split()) < 2:
                continue
            
            # Dédupliquer
            if query not in seen:
                cleaned.append(query)
                seen.add(query)
        
        return cleaned
    
    def _generate_fallback_queries(self, crawl_data: Dict[str, Any], num_queries: int) -> Dict[str, Any]:
        """Requêtes de fallback si l'analyse sémantique échoue"""
        
        url = crawl_data.get('url', '')
        domain = url.split('//')[1].split('/')[0] if '//' in url else url
        company_name = domain.split('.')[0].upper()
        
        fallback_queries = [
            f"{company_name} avis",
            f"meilleurs services {company_name}",
            f"{company_name} Québec",
            f"comment choisir {company_name}",
            f"{company_name} prix",
            f"comparatif {company_name}",
            f"guide {company_name}",
            f"{company_name} vs concurrent",
            "services professionnels Québec",
            "entreprise Québec",
            "meilleurs services Québec",
            "services entreprise Montréal",
            "comment choisir service professionnel",
            "prix services Québec",
            "comparatif services",
            "guide services 2025",
            "obtenir soumission Québec",
            "rendez-vous service Québec",
            "contact service professionnel",
            "devis gratuit Québec"
        ] * 5  # Répéter pour atteindre 100
        
        return {
            'queries': fallback_queries[:num_queries],
            'semantic_analysis': {
                'industry_classification': {'primary_industry': 'generic', 'confidence': 0.0},
                'entities': {},
                'topics': []
            },
            'breakdown': {
                'non_branded': 0,
                'semi_branded': 0,
                'branded': num_queries,
                'total': num_queries
            }
        }


# Fonction wrapper pour compatibilité
def generate_queries(crawl_data: Dict[str, Any], num_queries: int = 100) -> List[str]:
    """
    Fonction wrapper pour compatibilité avec l'ancien code
    
    Returns:
        Liste de requêtes uniquement (pour compatibilité)
    """
    generator = IntelligentQueryGeneratorV2()
    result = generator.generate_intelligent_queries(crawl_data, num_queries)
    return result.get('queries', [])


def generate_queries_with_analysis(crawl_data: Dict[str, Any], num_queries: int = 100) -> Dict[str, Any]:
    """
    Fonction complète qui retourne requêtes + analyse sémantique
    
    Returns:
        {
            'queries': [...],
            'semantic_analysis': {...},
            'breakdown': {...}
        }
    """
    generator = IntelligentQueryGeneratorV2()
    return generator.generate_intelligent_queries(crawl_data, num_queries)
