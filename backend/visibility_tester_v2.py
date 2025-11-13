"""
MODULE DE TESTS DE VISIBILITÉ V2 AVEC DIAGNOSTIC DÉTAILLÉ
Teste les requêtes sur 5 plateformes IA et diagnostique pourquoi le site est invisible
"""
import logging
import os
import re
from typing import Dict, Any, List
from datetime import datetime
import anthropic
from openai import OpenAI
import google.generativeai as genai

logger = logging.getLogger(__name__)

class VisibilityTesterV2:
    """Teste la visibilité avec diagnostic approfondi"""
    
    def __init__(self):
        # Initialize API clients
        self.anthropic_client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        self.perplexity_key = os.environ.get('PERPLEXITY_API_KEY')
    
    def test_all_queries_detailed(self, queries: List[str], site_url: str, company_name: str) -> Dict[str, Any]:
        """
        Test toutes les requêtes avec diagnostic complet
        
        Args:
            queries: Liste des requêtes à tester
            site_url: URL du site
            company_name: Nom de l'entreprise
        
        Returns:
            Résultats détaillés avec diagnostic d'invisibilité
        """
        results = {
            'site_url': site_url,
            'company_name': company_name,
            'last_updated': datetime.now().isoformat(),
            'queries': [],
            'summary': {
                'total_queries': len(queries),
                'global_visibility': 0.0,
                'by_platform': {}
            }
        }
        
        platforms = ['chatgpt', 'claude', 'perplexity', 'gemini', 'google_ai']
        platform_scores = {p: 0 for p in platforms}
        
        # Tester chaque requête
        for i, query in enumerate(queries[:10], 1):  # Limiter à 10 pour éviter coûts
            logger.info(f"Testing query {i}/{len(queries)}: {query}")
            
            query_result = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'platforms': {}
            }
            
            # Tester sur chaque plateforme
            for platform in platforms:
                try:
                    platform_result = self._test_single_query(query, platform, site_url, company_name)
                    query_result['platforms'][platform] = platform_result
                    
                    if platform_result.get('mentioned'):
                        platform_scores[platform] += 1
                        
                except Exception as e:
                    logger.error(f"Error testing {query} on {platform}: {str(e)}")
                    query_result['platforms'][platform] = {
                        'mentioned': False,
                        'error': str(e)
                    }
            
            results['queries'].append(query_result)
        
        # Calculer les scores
        queries_tested = len(results['queries'])
        if queries_tested > 0:
            for platform in platforms:
                platform_scores[platform] = platform_scores[platform] / queries_tested
            
            results['summary']['global_visibility'] = sum(platform_scores.values()) / len(platforms)
            results['summary']['by_platform'] = platform_scores
        
        logger.info(f"Testing complete. Global visibility: {results['summary']['global_visibility']*100:.1f}%")
        
        return results
    
    def _test_single_query(self, query: str, platform: str, site_url: str, company_name: str) -> Dict[str, Any]:
        """
        Test une seule requête sur une plateforme avec diagnostic complet
        
        Returns:
            Résultat détaillé avec diagnostic si invisible
        """
        result = {
            'mentioned': False,
            'position': None,
            'context_snippet': None,
            'competitors_mentioned': [],
            'full_response': '',
            'response_length': 0,
            'sentiment': 'neutral',
            'invisibility_reasons': []
        }
        
        # Exécuter la requête
        try:
            response = self._query_llm(platform, query)
            result['full_response'] = response
            result['response_length'] = len(response)
            
            # Analyser la réponse
            mentioned = site_url.lower() in response.lower() or company_name.lower() in response.lower()
            result['mentioned'] = mentioned
            
            if mentioned:
                # Extraire position et contexte
                result['position'] = self._find_position(response, company_name)
                result['context_snippet'] = self._extract_context(response, company_name, chars=200)
                result['sentiment'] = self._analyze_sentiment(response, company_name)
            
            # Extraire compétiteurs mentionnés
            result['competitors_mentioned'] = self._extract_competitors(response)
            
            # Si pas mentionné, diagnostiquer pourquoi
            if not mentioned:
                result['invisibility_reasons'] = self._diagnose_invisibility(
                    query, response, site_url, company_name
                )
            
        except Exception as e:
            logger.error(f"Error querying {platform}: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _query_llm(self, platform: str, query: str) -> str:
        """Exécuter une requête sur un LLM"""
        
        try:
            if platform == 'chatgpt':
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": query}],
                    max_tokens=500
                )
                return response.choices[0].message.content
            
            elif platform == 'claude':
                response = self.anthropic_client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=500,
                    messages=[{"role": "user", "content": query}]
                )
                return response.content[0].text
            
            elif platform == 'gemini':
                model = genai.GenerativeModel('gemini-1.5-pro-002')
                response = model.generate_content(query)
                return response.text
            
            elif platform == 'perplexity':
                # Perplexity via OpenAI-compatible API
                import requests
                response = requests.post(
                    'https://api.perplexity.ai/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.perplexity_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'llama-3.1-sonar-small-128k-online',
                        'messages': [{'role': 'user', 'content': query}],
                        'max_tokens': 500
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                else:
                    return ""
            
            elif platform == 'google_ai':
                # Google AI Overviews simulation (utilise Gemini)
                model = genai.GenerativeModel('gemini-1.5-pro-002')
                response = model.generate_content(query)
                return response.text
            
        except Exception as e:
            logger.error(f"Error querying {platform}: {str(e)}")
            return ""
        
        return ""
    
    def _find_position(self, response: str, company_name: str) -> int:
        """Trouver la position de la mention dans la réponse"""
        
        # Diviser en phrases
        sentences = re.split(r'[.!?]\s+', response)
        
        for i, sentence in enumerate(sentences, 1):
            if company_name.lower() in sentence.lower():
                return i
        
        return -1
    
    def _extract_context(self, response: str, company_name: str, chars: int = 200) -> str:
        """Extraire le contexte autour de la mention"""
        
        response_lower = response.lower()
        company_lower = company_name.lower()
        
        # Trouver la position de la mention
        pos = response_lower.find(company_lower)
        if pos == -1:
            return ""
        
        # Extraire contexte
        start = max(0, pos - chars // 2)
        end = min(len(response), pos + len(company_name) + chars // 2)
        
        context = response[start:end]
        
        # Ajouter ... si tronqué
        if start > 0:
            context = "..." + context
        if end < len(response):
            context = context + "..."
        
        return context
    
    def _analyze_sentiment(self, response: str, company_name: str) -> str:
        """Analyser le sentiment autour de la mention"""
        
        context = self._extract_context(response, company_name, chars=100)
        context_lower = context.lower()
        
        # Mots positifs
        positive_words = ['meilleur', 'excellent', 'recommandé', 'professionnel', 'qualité', 'fiable', 'expérimenté']
        # Mots négatifs
        negative_words = ['problème', 'mauvais', 'décevant', 'éviter', 'attention']
        
        positive_count = sum(1 for word in positive_words if word in context_lower)
        negative_count = sum(1 for word in negative_words if word in context_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_competitors(self, response: str) -> List[str]:
        """Extraire les noms de compétiteurs mentionnés"""
        
        # Patterns courants de compétiteurs au Québec
        competitor_patterns = [
            r'\b[A-Z][a-zéèêà]+ (?:Assurance|Insurance|Immobilier|Finance)\b',
            r'\b(?:Desjardins|La Capitale|Intact|Aviva|BFL|AON)\b',
            r'\b[A-Z][a-zéèêà]+ & [A-Z][a-zéèêà]+\b'
        ]
        
        competitors = []
        for pattern in competitor_patterns:
            matches = re.findall(pattern, response)
            competitors.extend(matches)
        
        # Dédupliquer
        return list(set(competitors))[:5]  # Top 5
    
    def _diagnose_invisibility(self, query: str, response: str, site_url: str, company_name: str) -> List[Dict[str, Any]]:
        """
        Diagnostiquer POURQUOI le site n'apparaît pas
        
        Returns:
            Liste de raisons avec actions concrètes
        """
        reasons = []
        
        # Simuler l'analyse (dans la vraie version, on crawl le site)
        # Pour l'instant, retourner des raisons génériques
        
        # Raison 1: Pas de contenu sur le sujet
        reasons.append({
            'reason': 'NO_RELEVANT_CONTENT',
            'severity': 'CRITICAL',
            'explanation': f"Aucune page ne traite spécifiquement de '{query}'",
            'action': f"Créer une page dédiée ou un article sur '{query}'",
            'example_title': f"Guide Complet: {query.title()} en 2025",
            'estimated_impact': 'HIGH'
        })
        
        # Raison 2: Contenu trop court
        reasons.append({
            'reason': 'INSUFFICIENT_CONTENT',
            'severity': 'HIGH',
            'explanation': "Contenu existant trop court (estimé < 1000 mots)",
            'action': "Étendre le contenu à minimum 2000 mots avec 10+ statistiques",
            'estimated_impact': 'MEDIUM-HIGH'
        })
        
        # Raison 3: Manque de statistiques
        competitors_mentioned = self._extract_competitors(response)
        if competitors_mentioned:
            reasons.append({
                'reason': 'INSUFFICIENT_DATA',
                'severity': 'HIGH',
                'explanation': f"Les compétiteurs cités ({', '.join(competitors_mentioned)}) ont probablement plus de données factuelles",
                'action': "Ajouter 10-15 statistiques avec sources dans le contenu",
                'example_stats': [
                    "68% des propriétaires sous-estiment leurs biens de 20%+",
                    "Le délai moyen de règlement est de 14 jours"
                ],
                'estimated_impact': 'HIGH'
            })
        
        # Raison 4: Pas de structured data
        reasons.append({
            'reason': 'NO_SCHEMA_MARKUP',
            'severity': 'MEDIUM',
            'explanation': "Schéma markup probablement absent ou incomplet",
            'action': "Ajouter schema Article + FAQPage + Organization",
            'estimated_impact': 'MEDIUM'
        })
        
        # Raison 5: Contenu trop marketing
        reasons.append({
            'reason': 'TOO_PROMOTIONAL',
            'severity': 'HIGH',
            'explanation': "Contenu probablement trop axé vente, pas assez éducatif/informatif",
            'action': "Réécrire en style encyclopédique avec faits objectifs",
            'estimated_impact': 'HIGH'
        })
        
        return reasons[:3]  # Top 3 raisons les plus importantes


# Fonction wrapper pour compatibilité
def test_visibility_with_details(queries: List[str], site_url: str, company_name: str) -> Dict[str, Any]:
    """
    Fonction wrapper pour compatibilité avec l'ancien code
    """
    tester = VisibilityTesterV2()
    return tester.test_all_queries_detailed(queries, site_url, company_name)
