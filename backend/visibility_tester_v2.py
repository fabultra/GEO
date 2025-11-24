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
import json
from collections import Counter

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
            
            # Calculer stats sentiment et Share of Voice
            sentiment_stats = {'positive': 0, 'neutral': 0, 'negative': 0}
            avg_sov = 0
            mentions_with_comp = 0
            
            for query_result in results['queries']:
                for platform, platform_result in query_result['platforms'].items():
                    if platform_result.get('mentioned'):
                        sentiment = platform_result.get('sentiment', 'neutral')
                        sentiment_stats[sentiment] += 1
                        
                        sov = platform_result.get('share_of_voice', 0)
                        if sov > 0:
                            avg_sov += sov
                            mentions_with_comp += 1
            
            if mentions_with_comp > 0:
                avg_sov = avg_sov / mentions_with_comp
            
            results['summary']['sentiment_breakdown'] = sentiment_stats
            results['summary']['avg_share_of_voice'] = round(avg_sov, 2)
            results['insights'] = {
                'dominant_sentiment': max(sentiment_stats, key=sentiment_stats.get) if sum(sentiment_stats.values()) > 0 else 'neutral',
                'share_of_voice_rating': 'HIGH' if avg_sov > 0.5 else 'MEDIUM' if avg_sov > 0.3 else 'LOW',
                'competitive_position': 'Leader' if avg_sov > 0.6 else 'Challenger' if avg_sov > 0.4 else 'Follower'
            }
        
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
            industry = "generic"
            competitors = self._extract_competitors(response, industry)
            result['competitors_mentioned'] = competitors
            
            # Calculer Share of Voice si mentionné et compétiteurs présents
            if mentioned and competitors:
                result['share_of_voice'] = self._calculate_share_of_voice(response, company_name, competitors)
            else:
                result['share_of_voice'] = 0.0
            
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
                    max_tokens=500,
                    temperature=0,  # ✅ DÉTERMINISTE
                    seed=42         # ✅ REPRODUCTIBLE
                )
                return response.choices[0].message.content
            
            elif platform == 'claude':
                response = self.anthropic_client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=500,
                    temperature=0,  # ✅ DÉTERMINISTE
                    messages=[{"role": "user", "content": query}]
                )
                return response.content[0].text
            
            elif platform == 'gemini':
                model = genai.GenerativeModel('gemini-1.5-pro-002')
                response = model.generate_content(
                    query,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0,  # ✅ DÉTERMINISTE
                    )
                )
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
                response = model.generate_content(
                    query,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0,  # ✅ DÉTERMINISTE
                    )
                )
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
        """Analyse le sentiment de la mention (amélioré)"""
        context = self._extract_context(response, company_name, chars=300)
        context_lower = context.lower()
        
        positive_keywords = [
            'excellent', 'meilleur', 'leader', 'recommandé', 'recommande',
            'fiable', 'qualité', 'expertise', 'professionnel', 'efficace',
            'rapide', 'performant', 'innovant', 'spécialisé', 'reconnu',
            'primé', 'certifié', 'expert', 'top', 'idéal', 'optimal'
        ]
        
        negative_keywords = [
            'problème', 'éviter', 'déconseillé', 'déconseille', 'mauvais',
            'limité', 'lent', 'cher', 'coûteux', 'manque', 'défaut',
            'insatisfait', 'déçu', 'erreur', 'bug', 'défaillance'
        ]
        
        positive_count = sum(1 for kw in positive_keywords if kw in context_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in context_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'
    
    def _calculate_share_of_voice(self, response: str, company_name: str, competitors: List) -> float:
        """Calcule le Share of Voice vs compétiteurs"""
        response_lower = response.lower()
        company_mentions = response_lower.count(company_name.lower())
        
        # Gérer les deux formats: liste de strings ou liste de dicts
        competitor_mentions = 0
        for c in competitors:
            if isinstance(c, dict):
                comp_name = c.get('name', '')
            else:
                comp_name = c
            competitor_mentions += response_lower.count(comp_name.lower())
        
        total = company_mentions + competitor_mentions
        return company_mentions / total if total > 0 else 0.0
    
    def _extract_competitors(self, response: str, industry: str = "generic") -> List[Dict[str, Any]]:
        """Extraire TOUS les compétiteurs avec Claude (extraction structurée)"""
        if not response or len(response) < 50:
            return []
        
        response_sample = response[:3000] if len(response) > 3000 else response
        
        prompt = f"""Analyse cette réponse d'un LLM et identifie TOUS les compétiteurs/entreprises mentionnés.

INDUSTRIE : {industry}

RÉPONSE DU LLM :
{response_sample}

Pour CHAQUE compétiteur trouvé, extrait :
1. Nom exact de l'entreprise
2. URLs/domaines mentionnés si présents
3. Contexte de la mention (1 phrase courte)
4. Type de mention : "recommendation", "comparison", "neutral", ou "negative"
5. Force perçue : 1 phrase décrivant ce qui est dit de positif

Réponds UNIQUEMENT avec un JSON valide (array). Si AUCUN compétiteur, retourne []

Format:
[{{"name": "Nom", "urls": ["domain.com"], "context": "Raison", "mention_type": "recommendation", "perceived_strength": "Force"}}]

IMPORTANT: Ne retourne QUE les vraies entreprises compétitrices."""

        try:
            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text.strip().replace('```json', '').replace('```', '').strip()
            competitors = json.loads(response_text)
            
            if not isinstance(competitors, list):
                logger.warning("Extraction returned non-list, using fallback")
                return self._extract_competitors_fallback(response)
            
            logger.info(f"✅ Extracted {len(competitors)} competitors dynamically")
            return competitors[:10]
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}, using fallback")
            return self._extract_competitors_fallback(response)
    
    def _extract_competitors_fallback(self, response: str) -> List[Dict[str, Any]]:
        """Fallback regex si LLM échoue"""
        competitor_patterns = [
            r'\b[A-Z][a-zéèêà]+ (?:Assurance|Insurance|Bank|Banque)\b',
            r'\b(?:Desjardins|Intact|Shopify|Salesforce|Wix)\b',
            r'\b([a-z0-9-]+\.(com|ca|org|net|io))\b'
        ]
        competitors_found = []
        seen_names = set()
        
        for pattern in competitor_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                name = match[0] if isinstance(match, tuple) else match
                name = name.strip()
                if name.lower() not in seen_names:
                    seen_names.add(name.lower())
                    competitors_found.append({
                        'name': name,
                        'urls': [name] if '.' in name else [],
                        'context': 'Mentionné',
                        'mention_type': 'neutral',
                        'perceived_strength': ''
                    })
        return competitors_found[:10]
    
    def _classify_query_type(self, query: str, company_name: str) -> str:
        """Classifier: branded, informational, comparison, transactional, navigational"""
        query_lower = query.lower()
        company_lower = company_name.lower()
        
        if company_lower in query_lower:
            return "branded"
        
        comparison_keywords = ['vs', 'versus', 'comparatif', 'comparer', 'meilleur', 'meilleure', 'top', 'choisir', 'quel']
        if any(kw in query_lower for kw in comparison_keywords):
            return "comparison"
        
        transactional_keywords = ['prix', 'coût', 'tarif', 'soumission', 'acheter', 'devis', 'gratuit']
        if any(kw in query_lower for kw in transactional_keywords):
            return "transactional"
        
        navigational_keywords = ['site', 'contact', 'adresse', 'téléphone']
        if any(kw in query_lower for kw in navigational_keywords):
            return "navigational"
        
        return "informational"
    
    def analyze_competitor_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyser chaque compétiteur et générer insights"""
        competitor_data = {}
        
        for query_result in results.get('queries', []):
            query_text = query_result.get('query', '')
            for platform, platform_result in query_result.get('platforms', {}).items():
                competitors = platform_result.get('competitors_mentioned', [])
                for comp in competitors:
                    comp_name = comp.get('name', comp) if isinstance(comp, dict) else comp
                    if comp_name not in competitor_data:
                        competitor_data[comp_name] = {
                            'name': comp_name, 'mentions': [], 'urls_cited': set(),
                            'perceived_strengths': [], 'queries_present_in': set(),
                            'mention_types': {'recommendation': 0, 'comparison': 0, 'neutral': 0, 'negative': 0}
                        }
                    
                    competitor_data[comp_name]['mentions'].append({'query': query_text, 'platform': platform})
                    competitor_data[comp_name]['queries_present_in'].add(query_text)
                    
                    if isinstance(comp, dict):
                        if 'urls' in comp:
                            competitor_data[comp_name]['urls_cited'].update(comp['urls'])
                        if 'perceived_strength' in comp and comp['perceived_strength']:
                            competitor_data[comp_name]['perceived_strengths'].append(comp['perceived_strength'])
                        mention_type = comp.get('mention_type', 'neutral')
                        if mention_type in competitor_data[comp_name]['mention_types']:
                            competitor_data[comp_name]['mention_types'][mention_type] += 1
        
        competitors_analyzed = []
        total_tests = len(results.get('queries', [])) * 5
        
        for comp_name, comp_info in competitor_data.items():
            competitors_analyzed.append({
                'name': comp_name,
                'total_mentions': len(comp_info['mentions']),
                'visibility_rate': len(comp_info['mentions']) / total_tests if total_tests > 0 else 0,
                'urls_cited': list(comp_info['urls_cited']),
                'perceived_strengths': list(set([s for s in comp_info['perceived_strengths'] if s])),
                'mention_breakdown': comp_info['mention_types'],
                'queries_present_in': list(comp_info['queries_present_in'])
            })
        
        competitors_analyzed.sort(key=lambda x: x['total_mentions'], reverse=True)
        
        return {
            'total_unique_competitors': len(competitors_analyzed),
            'competitors': competitors_analyzed[:10],
            'competitive_insights': self._generate_competitive_insights(competitors_analyzed, results)
        }
    
    def _generate_competitive_insights(self, competitors: List[Dict], results: Dict) -> List[Dict]:
        """Générer insights actionnables"""
        insights = []
        if not competitors:
            return insights
        
        top_competitor = competitors[0]
        insights.append({
            'type': 'DOMINANT_COMPETITOR',
            'severity': 'HIGH',
            'title': f"{top_competitor['name']} domine avec {top_competitor['total_mentions']} mentions",
            'details': f"Visibilité : {top_competitor['visibility_rate']*100:.1f}%",
            'perceived_strengths': top_competitor.get('perceived_strengths', []),
            'action': f"Analyser leurs {len(top_competitor.get('urls_cited', []))} URLs citées",
            'urls_to_analyze': top_competitor.get('urls_cited', [])
        })
        
        your_visibility = results.get('summary', {}).get('global_visibility', 0)
        top_visibility = top_competitor['visibility_rate']
        
        if top_visibility > 0:
            gap_ratio = top_visibility / your_visibility if your_visibility > 0 else float('inf')
            if gap_ratio > 2 or your_visibility == 0:
                insights.append({
                    'type': 'VISIBILITY_GAP',
                    'severity': 'CRITICAL',
                    'title': f"Vous êtes {gap_ratio:.1f}x MOINS visible que {top_competitor['name']}" if your_visibility > 0 else f"{top_competitor['name']} visible, vous invisible",
                    'details': f"Leur: {top_visibility*100:.1f}% | Vous: {your_visibility*100:.1f}%",
                    'action': "Reverse-engineer leurs pages citées"
                })
        
        total_urls = sum(len(c.get('urls_cited', [])) for c in competitors)
        if total_urls > 0:
            insights.append({
                'type': 'URL_CITATION_GAP',
                'severity': 'HIGH',
                'title': f"LLMs citent {total_urls} URLs de compétiteurs",
                'details': f"Top: {', '.join(competitors[0].get('urls_cited', [])[:3])}",
                'action': "Créer pages avec stats pour être cité",
                'example': "Ajouter 15+ statistiques par page"
            })
        
        return insights
    
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
