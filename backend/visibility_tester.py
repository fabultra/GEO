"""
Module pour tester la visibilité d'un site dans les moteurs IA génératifs
"""
import os
import asyncio
import logging
from typing import Dict, List, Any
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
import requests

logger = logging.getLogger(__name__)

class VisibilityTester:
    """Teste la visibilité d'un site dans 5 plateformes IA"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.anthropic_client = AsyncAnthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        self.perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY')
        
        # Configure Gemini
        gemini_key = os.environ.get('GEMINI_API_KEY')
        if gemini_key:
            genai.configure(api_key=gemini_key)
    
    async def test_chatgpt(self, query: str, site_url: str) -> Dict[str, Any]:
        """Test visibilité dans ChatGPT avec analyse détaillée"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Vous êtes un assistant qui répond aux questions avec des sources."},
                    {"role": "user", "content": query}
                ],
                temperature=0,  # ✅ DÉTERMINISTE
                seed=42,        # ✅ REPRODUCTIBLE
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Vérifier si le site est mentionné
            site_domain = site_url.replace('https://', '').replace('http://', '').split('/')[0]
            site_name = site_domain.split('.')[0].capitalize()
            is_mentioned = site_domain.lower() in answer.lower() or site_name.lower() in answer.lower()
            
            # Analyse détaillée si mentionné
            position = None
            context = None
            sentiment = "neutral"
            competitors_found = []
            
            if is_mentioned:
                # Trouver la position (1er, 2ème, 3ème...)
                sentences = answer.split('.')
                for i, sentence in enumerate(sentences, 1):
                    if site_domain.lower() in sentence.lower() or site_name.lower() in sentence.lower():
                        position = i
                        context = sentence.strip()
                        break
                
                # Analyser le sentiment
                if any(word in context.lower() for word in ['meilleur', 'excellent', 'recommandé', 'leader', 'qualité']):
                    sentiment = "positive"
                elif any(word in context.lower() for word in ['mais', 'cependant', 'limité', 'cher']):
                    sentiment = "mixed"
                
                # Identifier compétiteurs mentionnés
                common_competitors = ['desjardins', 'lacapitale', 'intact', 'industrielle', 'ssq', 'bfl', 'aon']
                for comp in common_competitors:
                    if comp in answer.lower():
                        competitors_found.append(comp.capitalize())
            
            return {
                "platform": "ChatGPT",
                "query": query,
                "mentioned": is_mentioned,
                "position": position,
                "context": context,
                "sentiment": sentiment,
                "competitors_found": competitors_found,
                "answer": answer,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"ChatGPT test error: {str(e)}")
            return {
                "platform": "ChatGPT",
                "query": query,
                "mentioned": False,
                "error": str(e)
            }
    
    async def test_claude(self, query: str, site_url: str) -> Dict[str, Any]:
        """Test visibilité dans Claude"""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=500,
                temperature=0,  # ✅ DÉTERMINISTE
                messages=[
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            )
            
            answer = response.content[0].text
            
            # Vérifier si le site est mentionné
            site_domain = site_url.replace('https://', '').replace('http://', '').split('/')[0]
            is_mentioned = site_domain.lower() in answer.lower()
            
            return {
                "platform": "Claude",
                "query": query,
                "mentioned": is_mentioned,
                "answer": answer,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
            
        except Exception as e:
            logger.error(f"Claude test error: {str(e)}")
            return {
                "platform": "Claude",
                "query": query,
                "mentioned": False,
                "error": str(e)
            }
    
    async def test_perplexity(self, query: str, site_url: str) -> Dict[str, Any]:
        """Test visibilité dans Perplexity"""
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3,
                "return_citations": True
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            answer = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            # Vérifier si le site est mentionné
            site_domain = site_url.replace('https://', '').replace('http://', '').split('/')[0]
            is_mentioned = site_domain.lower() in answer.lower()
            
            # Vérifier dans les citations
            cited = any(site_domain.lower() in citation.lower() for citation in citations)
            
            return {
                "platform": "Perplexity",
                "query": query,
                "mentioned": is_mentioned or cited,
                "answer": answer,
                "citations": citations,
                "cited": cited
            }
            
        except Exception as e:
            logger.error(f"Perplexity test error: {str(e)}")
            return {
                "platform": "Perplexity",
                "query": query,
                "mentioned": False,
                "error": str(e)
            }
    
    async def test_gemini(self, query: str, site_url: str) -> Dict[str, Any]:
        """Test visibilité dans Gemini"""
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            response = model.generate_content(
                query,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )
            
            answer = response.text
            
            # Vérifier si le site est mentionné
            site_domain = site_url.replace('https://', '').replace('http://', '').split('/')[0]
            is_mentioned = site_domain.lower() in answer.lower()
            
            return {
                "platform": "Gemini",
                "query": query,
                "mentioned": is_mentioned,
                "answer": answer
            }
            
        except Exception as e:
            logger.error(f"Gemini test error: {str(e)}")
            return {
                "platform": "Gemini",
                "query": query,
                "mentioned": False,
                "error": str(e)
            }
    
    async def test_google_ai_overviews(self, query: str, site_url: str) -> Dict[str, Any]:
        """Test visibilité dans Google AI Overviews (scraping simulé)"""
        # Note: Pas d'API publique, on simule pour l'instant
        # En production, utiliser un service de scraping comme ScraperAPI
        try:
            logger.info(f"Google AI Overviews: simulation pour {query}")
            
            # Pour l'instant, on retourne un résultat simulé
            # Dans une vraie implémentation, il faudrait scraper Google avec l'API ScraperAPI
            return {
                "platform": "Google AI Overviews",
                "query": query,
                "mentioned": False,
                "answer": "Simulation - API non disponible",
                "note": "Google AI Overviews nécessite du web scraping"
            }
            
        except Exception as e:
            logger.error(f"Google AI Overviews test error: {str(e)}")
            return {
                "platform": "Google AI Overviews",
                "query": query,
                "mentioned": False,
                "error": str(e)
            }
    
    async def test_all_platforms(self, query: str, site_url: str) -> List[Dict[str, Any]]:
        """Test toutes les plateformes pour une requête"""
        tasks = [
            self.test_chatgpt(query, site_url),
            self.test_claude(query, site_url),
            self.test_perplexity(query, site_url),
            self.test_gemini(query, site_url),
            self.test_google_ai_overviews(query, site_url)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrer les exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Platform test failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def test_visibility(self, site_url: str, queries: List[str]) -> Dict[str, Any]:
        """
        Test la visibilité d'un site sur toutes les plateformes avec plusieurs requêtes
        
        Returns:
            {
                'overall_visibility': 0.0-1.0,
                'platform_scores': {
                    'ChatGPT': 0.0-1.0,
                    'Claude': 0.0-1.0,
                    ...
                },
                'details': [...]
            }
        """
        all_results = []
        
        # Limiter à 10 requêtes pour éviter les coûts élevés
        test_queries = queries[:10]
        
        logger.info(f"Testing visibility for {site_url} with {len(test_queries)} queries")
        
        for query in test_queries:
            results = await self.test_all_platforms(query, site_url)
            all_results.extend(results)
            
            # Petit délai entre les requêtes
            await asyncio.sleep(1)
        
        # Calculer les scores par plateforme
        platform_scores = {}
        platforms = ["ChatGPT", "Claude", "Perplexity", "Gemini", "Google AI Overviews"]
        
        for platform in platforms:
            platform_results = [r for r in all_results if r.get('platform') == platform]
            if platform_results:
                mentions = sum(1 for r in platform_results if r.get('mentioned', False))
                platform_scores[platform] = mentions / len(platform_results)
            else:
                platform_scores[platform] = 0.0
        
        # Score global
        overall_visibility = sum(platform_scores.values()) / len(platform_scores)
        
        return {
            'overall_visibility': overall_visibility,
            'platform_scores': platform_scores,
            'queries_tested': len(test_queries),
            'total_tests': len(all_results),
            'details': all_results
        }
