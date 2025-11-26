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
        """Génère des requêtes de recherche Google ciblées"""
        queries = []
        
        # Déterminer la localisation
        location = ""
        if geographic_scope in ['local', 'regional']:
            location = "Canada"  # Adapter selon le contexte
        elif geographic_scope == 'national':
            location = "Canada"
        
        # Query 1: Industrie + type + top companies
        if sub_industry:
            queries.append(f"top {sub_industry} {company_type} companies {location}")
        else:
            queries.append(f"top {primary_industry} {company_type} companies {location}")
        
        # Query 2: Services/produits principaux
        if offerings:
            main_offering = offerings[0]
            queries.append(f"best {main_offering} providers {location}")
        
        # Query 3: Industrie + leaders
        queries.append(f"{primary_industry} industry leaders {location}")
        
        # Query 4: Alternative générique
        queries.append(f"{primary_industry} companies list {location}")
        
        return queries
    
    def _search_google(self, query: str, max_results: int = 10) -> List[str]:
        """
        Recherche sur Google et extrait les URLs des résultats
        
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
            
            # Extraire les URLs des résultats de recherche
            # Google utilise différents sélecteurs selon les versions
            result_divs = soup.find_all('div', class_='g')
            
            for div in result_divs:
                # Chercher le lien
                link = div.find('a', href=True)
                if link:
                    url = link['href']
                    
                    # Nettoyer l'URL (Google ajoute parfois des préfixes)
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    # Vérifier que c'est une vraie URL
                    if url.startswith('http') and self._is_valid_competitor_url(url):
                        urls.append(url)
            
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
