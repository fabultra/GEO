"""
Service de découverte intelligente de compétiteurs RÉELS
Utilise l'analyse sémantique + recherche Google pour identifier les vrais acteurs du marché
Inspiré de searchable.com
"""
import logging
import requests
import re
from typing import List, Dict, Any, Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote_plus
import time

logger = logging.getLogger(__name__)


class CompetitorDiscovery:
    """Découvre de vrais compétiteurs basés sur l'analyse sémantique"""
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.google_delay = 2  # Délai entre requêtes Google
        
    def discover_real_competitors(
        self, 
        semantic_analysis: Dict[str, Any],
        our_url: str,
        max_competitors: int = 5
    ) -> List[str]:
        """
        Découvre de vrais compétiteurs basés sur l'analyse sémantique
        
        Args:
            semantic_analysis: Résultat de l'analyse sémantique
            our_url: Notre URL (à exclure)
            max_competitors: Nombre max de compétiteurs
            
        Returns:
            Liste d'URLs de compétiteurs réels et validées
        """
        logger.info("🔍 Starting intelligent competitor discovery...")
        
        # Extraire les informations clés
        industry_info = semantic_analysis.get('industry_classification', {})
        primary_industry = industry_info.get('primary_industry', '')
        sub_industry = industry_info.get('sub_industry', '')
        company_type = industry_info.get('company_type', '')
        geographic_scope = industry_info.get('geographic_scope', 'national')
        
        # Extraire les offerings principaux
        entities = semantic_analysis.get('entities', {})
        offerings = entities.get('offerings', [])
        top_offerings = [o.get('name') if isinstance(o, dict) else str(o) for o in offerings[:3]]
        
        logger.info(f"📊 Industry: {primary_industry} | Sub: {sub_industry} | Type: {company_type}")
        logger.info(f"🎯 Top offerings: {', '.join(top_offerings)}")
        
        # Générer des requêtes de recherche intelligentes
        search_queries = self._generate_search_queries(
            primary_industry=primary_industry,
            sub_industry=sub_industry,
            company_type=company_type,
            offerings=top_offerings,
            geographic_scope=geographic_scope
        )
        
        # Rechercher sur Google
        competitor_urls = set()
        for query in search_queries[:3]:  # Limiter à 3 requêtes max
            logger.info(f"🔎 Google search: {query}")
            urls = self._search_google(query, max_results=10)
            competitor_urls.update(urls)
            
            if len(competitor_urls) >= max_competitors * 2:
                break
            
            time.sleep(self.google_delay)  # Respecter les limites
        
        # FALLBACK: Si Google ne retourne rien, utiliser Claude
        if len(competitor_urls) == 0:
            logger.warning("⚠️  Google search returned 0 results, using Claude fallback")
            competitor_urls = set(self._get_competitors_from_claude(
                primary_industry=primary_industry,
                sub_industry=sub_industry,
                company_type=company_type,
                max_competitors=max_competitors
            ))
        
        # Filtrer notre propre domaine
        our_domain = self._extract_domain(our_url)
        competitor_urls = [
            url for url in competitor_urls 
            if self._extract_domain(url) != our_domain
        ]
        
        # Valider et scorer les URLs
        validated_competitors = self._validate_and_score_competitors(
            competitor_urls,
            primary_industry=primary_industry,
            offerings=top_offerings
        )
        
        # Retourner les top N
        top_competitors = validated_competitors[:max_competitors]
        
        logger.info(f"✅ Found {len(top_competitors)} real competitors")
        for i, comp in enumerate(top_competitors, 1):
            logger.info(f"  {i}. {comp['url']} (score: {comp['score']:.2f})")
        
        return [c['url'] for c in top_competitors]
    
    def _generate_search_queries(
        self,
        primary_industry: str,
        sub_industry: str,
        company_type: str,
        offerings: List[str],
        geographic_scope: str
    ) -> List[str]:
        """Génère des requêtes de recherche Google BILINGUES (FR + EN) pour le Québec/Canada"""
        queries = []
        
        # Localisation pour Québec/Canada
        location_fr = "Québec"
        location_en = "Quebec Canada"
        
        # Simplifier les noms d'industrie
        industry_clean = primary_industry.replace('_', ' ').strip().lower()
        sub_clean = sub_industry.replace('_', ' ').strip().lower() if sub_industry else ""
        
        # Choisir la meilleure industrie
        industry_to_use = sub_clean if (sub_clean and len(sub_clean) < 40) else industry_clean
        
        # Traductions françaises NATURELLES pour industries (expressions québécoises)
        industry_translations = {
            'insurance': 'compagnie d\'assurance',
            'life insurance': 'assurance vie',
            'car insurance': 'assurance auto',
            'home insurance': 'assurance habitation',
            'financial services': 'services financiers',
            'banking': 'institution bancaire',
            'real estate': 'immobilier',
            'construction': 'construction',
            'technology': 'entreprise technologie',
            'healthcare': 'services santé',
            'education': 'éducation',
            'retail': 'commerce détail',
            'manufacturing': 'manufacturier',
            'consulting': 'firme consultation',
            'legal services': 'cabinet avocat',
            'accounting': 'cabinet comptable'
        }
        
        # Termes génériques en français
        generic_terms_fr = {
            'insurance': 'assureur',
            'financial': 'financière',
            'technology': 'techno',
            'consulting': 'conseil',
            'service': 'service'
        }
        
        # Traduire l'industrie vers le français naturel
        industry_fr = None
        for en, fr in industry_translations.items():
            if en in industry_to_use:
                industry_fr = fr
                break
        
        # Si pas de traduction exacte, utiliser terme générique
        if not industry_fr:
            for en, fr in generic_terms_fr.items():
                if en in industry_to_use:
                    industry_fr = fr
                    break
        
        # Fallback: garder l'original si aucune traduction
        if not industry_fr:
            industry_fr = industry_to_use
        
        # REQUÊTES EN FRANÇAIS (naturel québécois)
        # Adapter selon le type d'industrie (avec ou sans "compagnie")
        if any(term in industry_fr for term in ['compagnie', 'cabinet', 'firme', 'institution']):
            # Déjà un nom complet (ex: "compagnie d'assurance")
            queries.append(f"meilleures {industry_fr} {location_fr}")
            queries.append(f"top {industry_fr} Québec")
        elif any(term in industry_fr for term in ['assurance', 'assureur', 'financière']):
            # Ajouter "compagnie" ou terme approprié
            queries.append(f"meilleures compagnies {industry_fr} {location_fr}")
            queries.append(f"top compagnies {industry_fr} Québec")
        else:
            # Terme générique - ajouter "entreprise"
            queries.append(f"meilleures entreprises {industry_fr} {location_fr}")
            queries.append(f"top entreprises {industry_fr} Québec")
        
        # Liste générale
        queries.append(f"liste {industry_fr} Canada")
        
        # REQUÊTES EN ANGLAIS (Canada)
        queries.append(f"top {industry_to_use} companies {location_en}")
        queries.append(f"best {industry_to_use} {location_en}")
        
        # Services/produits spécifiques en français
        if offerings and len(offerings[0]) < 40:
            main_offering = offerings[0]
            queries.append(f"{main_offering} {location_fr}")
        
        return queries
    
    def _search_google(self, query: str, max_results: int = 10) -> List[str]:
        """
        Recherche sur Google et extrait les URLs des résultats
        Utilise plusieurs méthodes de parsing pour robustesse
        
        Args:
            query: Requête de recherche
            max_results: Nombre max de résultats
            
        Returns:
            Liste d'URLs
        """
        urls = []
        
        try:
            # Construire l'URL de recherche Google
            encoded_query = quote_plus(query)
            google_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"
            
            # Faire la requête
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(google_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parser les résultats
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Méthode 1: Chercher tous les liens <a>
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                
                # Nettoyer et extraire l'URL
                if '/url?q=' in href:
                    # Format: /url?q=https://example.com&sa=...
                    try:
                        url = href.split('/url?q=')[1].split('&')[0]
                        if url.startswith('http') and self._is_valid_competitor_url(url):
                            urls.append(url)
                    except:
                        pass
                elif href.startswith('http') and self._is_valid_competitor_url(href):
                    # URL directe
                    urls.append(href)
            
            # Dédupliquer
            urls = list(dict.fromkeys(urls))  # Garde l'ordre
            
            logger.info(f"  → Found {len(urls)} URLs from Google")
            
        except Exception as e:
            logger.warning(f"Failed to search Google for '{query}': {e}")
        
        return urls
    
    def _is_valid_competitor_url(self, url: str) -> bool:
        """Filtre les URLs non pertinentes (réseaux sociaux, etc.)"""
        # Exclure les domaines non pertinents
        excluded_domains = [
            'google.com', 'facebook.com', 'twitter.com', 'linkedin.com',
            'instagram.com', 'youtube.com', 'wikipedia.org', 'yelp.com',
            'maps.google.com', 'amazon.com', 'ebay.com'
        ]
        
        domain = self._extract_domain(url)
        
        for excluded in excluded_domains:
            if excluded in domain:
                return False
        
        return True
    
    def _extract_domain(self, url: str) -> str:
        """Extrait le domaine d'une URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain.replace('www.', '')
        except:
            return url
    
    def _get_competitors_from_claude(
        self,
        primary_industry: str,
        sub_industry: str,
        company_type: str,
        max_competitors: int = 5
    ) -> List[str]:
        """
        Fallback: Demander à Claude de suggérer des compétiteurs (bilingue FR/EN)
        
        Returns:
            Liste d'URLs suggérées
        """
        try:
            import os
            from anthropic import Anthropic
            
            # Utiliser ANTHROPIC_API_KEY ou EMERGENT_LLM_KEY
            api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('EMERGENT_LLM_KEY')
            if not api_key:
                logger.error("No API key found for Claude (ANTHROPIC_API_KEY or EMERGENT_LLM_KEY)")
                return []
            
            anthropic_client = Anthropic(api_key=api_key)
            
            # Simplifier pour Claude
            industry_desc = sub_industry if sub_industry else primary_industry
            
            prompt = f"""Suggère {max_competitors} URLs de sites web de compétiteurs majeurs pour une entreprise dans l'industrie "{industry_desc}" au Québec/Canada.

IMPORTANT: Inclure des compétiteurs francophones québécois ET anglophones canadiens.

Réponds UNIQUEMENT avec un JSON valide:
{{
  "competitors": ["https://competitor1.com", "https://competitor2.com", ...]
}}

URLs seulement, pas d'explication."""
            
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Nettoyer markdown
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            import json
            result = json.loads(response_text.strip())
            competitors = result.get('competitors', [])[:max_competitors]
            
            logger.info(f"✅ Claude suggested {len(competitors)} competitors")
            return competitors
            
        except Exception as e:
            logger.error(f"Failed to get competitors from Claude: {e}")
            return []
    
    def _validate_and_score_competitors(
        self,
        urls: List[str],
        primary_industry: str,
        offerings: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Valide et score les URLs de compétiteurs
        
        Returns:
            Liste triée par score décroissant
        """
        competitors = []
        
        for url in urls:
            try:
                # Validation basique (HEAD request)
                response = requests.head(url, timeout=5, allow_redirects=True)
                
                if response.status_code < 400:
                    # Score basé sur plusieurs critères
                    score = self._calculate_relevance_score(
                        url=url,
                        primary_industry=primary_industry,
                        offerings=offerings
                    )
                    
                    competitors.append({
                        'url': url,
                        'score': score,
                        'domain': self._extract_domain(url)
                    })
                    
            except Exception as e:
                logger.debug(f"Skipped {url}: {e}")
                continue
        
        # Trier par score décroissant
        competitors.sort(key=lambda x: x['score'], reverse=True)
        
        return competitors
    
    def _calculate_relevance_score(
        self,
        url: str,
        primary_industry: str,
        offerings: List[str]
    ) -> float:
        """
        Calculate un score de pertinence pour un compétiteur
        
        Returns:
            Score entre 0 et 1
        """
        score = 0.5  # Score de base
        
        url_lower = url.lower()
        domain = self._extract_domain(url)
        
        # Bonus si l'industrie est dans l'URL/domaine
        industry_keywords = primary_industry.lower().split()
        for keyword in industry_keywords:
            if len(keyword) > 3:  # Ignorer les mots courts
                if keyword in url_lower or keyword in domain:
                    score += 0.1
        
        # Bonus si un offering est dans l'URL/domaine
        for offering in offerings:
            if offering:
                offering_lower = offering.lower()
                if offering_lower in url_lower or offering_lower in domain:
                    score += 0.15
        
        # Pénalité pour les domaines génériques
        generic_terms = ['info', 'web', 'site', 'portal', 'directory']
        for term in generic_terms:
            if term in domain:
                score -= 0.1
        
        # Cap entre 0 et 1
        return max(0.0, min(1.0, score))


# Instance globale
competitor_discovery = CompetitorDiscovery()
