"""
Service de découverte intelligente de compétiteurs RÉELS
Pipeline complet en 3 étages sans code incomplet
Version 2 - Production ready
"""
import logging
import requests
import socket
import time
import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote_plus
from collections import Counter

logger = logging.getLogger(__name__)


class CompetitorDiscovery:
    """
    Découvre de vrais compétiteurs via pipeline 3 étages:
    1. Extraction depuis visibilité/LLM (via CompetitorExtractor)
    2. Recherche web structurée (Google + fallback Claude)
    3. Validation, scoring et sélection finale
    """
    
    def __init__(self):
        from config import (
            COMPETITOR_SEARCH_TIMEOUT,
            COMPETITOR_SEARCH_DELAY,
            COMPETITOR_VALIDATION_TIMEOUT,
            COMPETITOR_MAX_RETRIES,
            COMPETITOR_RELEVANCE_THRESHOLD_DIRECT,
            COMPETITOR_RELEVANCE_THRESHOLD_INDIRECT,
            MAX_COMPETITORS
        )
        
        self.search_timeout = COMPETITOR_SEARCH_TIMEOUT
        self.search_delay = COMPETITOR_SEARCH_DELAY
        self.validation_timeout = COMPETITOR_VALIDATION_TIMEOUT
        self.max_retries = COMPETITOR_MAX_RETRIES
        self.threshold_direct = COMPETITOR_RELEVANCE_THRESHOLD_DIRECT
        self.threshold_indirect = COMPETITOR_RELEVANCE_THRESHOLD_INDIRECT
        self.max_competitors = MAX_COMPETITORS
        
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    def discover_real_competitors(
        self,
        semantic_analysis: Dict[str, Any],
        our_url: str,
        visibility_urls: Optional[List[str]] = None,
        max_competitors: int = None
    ) -> List[Dict[str, Any]]:
        """
        Point d'entrée principal : découvre des compétiteurs réels et pertinents
        
        Pipeline complet:
        1. Combine URLs depuis visibilité (visibility_urls) + recherche web
        2. Valide existence et accessibilité
        3. Score pertinence (0-1) et classe direct/indirect
        4. Retourne top N triés par score
        
        Args:
            semantic_analysis: Analyse sémantique du site (industrie, offerings, etc.)
            our_url: URL de notre site (à exclure)
            visibility_urls: URLs déjà extraites depuis visibilité/LLM (optionnel)
            max_competitors: Nombre max (défaut: config.MAX_COMPETITORS)
            
        Returns:
            Liste de dicts:
            [
                {
                    'domain': 'competitor.com',
                    'homepage_url': 'https://competitor.com',
                    'score': 0.85,
                    'type': 'direct',  # ou 'indirect'
                    'reason': 'Même industrie (assurance), offerings similaires',
                    'source': 'both'  # 'llm', 'web_search', 'both'
                },
                ...
            ]
        """
        if max_competitors is None:
            max_competitors = self.max_competitors
        
        logger.info("🚀 Starting complete competitor discovery pipeline...")
        
        # Extraire infos clés du semantic_analysis
        industry_info = semantic_analysis.get('industry_classification', {})
        primary_industry = industry_info.get('primary_industry', '')
        sub_industry = industry_info.get('sub_industry', '')
        company_type = industry_info.get('company_type', '')
        
        entities = semantic_analysis.get('entities', {})
        offerings = entities.get('offerings', [])
        top_offerings = [o.get('name') if isinstance(o, dict) else str(o) for o in offerings[:3]]
        
        # Extraire brand name depuis URL ou title
        brand_name = self._extract_brand_name(our_url, semantic_analysis)
        
        logger.info(f"📊 Target: {brand_name} | Industry: {primary_industry} | Offerings: {top_offerings[:2]}")
        
        # STAGE 1 déjà fait en amont (visibility_urls)
        # STAGE 2: Recherche web
        web_urls = self._search_web_for_competitors(
            our_url=our_url,
            primary_industry=primary_industry,
            sub_industry=sub_industry,
            offerings=top_offerings,
            brand_name=brand_name
        )
        
        # Combiner URLs des 2 sources
        all_candidate_urls = list(set((visibility_urls or []) + web_urls))
        
        # Marquer la source de chaque URL
        url_sources = {}
        for url in visibility_urls or []:
            url_sources[url] = 'llm'
        for url in web_urls:
            if url in url_sources:
                url_sources[url] = 'both'
            else:
                url_sources[url] = 'web_search'
        
        logger.info(f"📥 Total candidates: {len(all_candidate_urls)} (LLM: {len(visibility_urls or [])}, Web: {len(web_urls)})")
        
        # Filtrer notre propre domaine
        from utils.competitor_extractor import CompetitorExtractor
        filtered_urls = CompetitorExtractor.filter_self_domain(all_candidate_urls, our_url)
        
        # STAGE 3: Validation et scoring
        scored_competitors = self._validate_and_score_competitors(
            urls=filtered_urls,
            our_url=our_url,
            primary_industry=primary_industry,
            offerings=top_offerings,
            url_sources=url_sources
        )
        
        # Trier par score décroissant et limiter
        scored_competitors.sort(key=lambda x: x['score'], reverse=True)
        top_competitors = scored_competitors[:max_competitors]
        
        logger.info(f"✅ Final: {len(top_competitors)} competitors (direct: {sum(1 for c in top_competitors if c['type']=='direct')}, indirect: {sum(1 for c in top_competitors if c['type']=='indirect')})")
        
        return top_competitors
    
    def _extract_brand_name(self, url: str, semantic_analysis: Dict) -> str:
        """
        Extrait le nom de marque depuis l'URL ou l'analyse sémantique
        """
        # Essayer depuis semantic_analysis
        company_desc = semantic_analysis.get('company_description', {})
        brand = company_desc.get('brand_name', '')
        if brand:
            return brand
        
        # Fallback: depuis domain
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            # Prendre la partie avant le TLD
            brand = domain.split('.')[0]
            return brand.capitalize()
        except:
            return ''
    
    def _search_web_for_competitors(
        self,
        our_url: str,
        primary_industry: str,
        sub_industry: str,
        offerings: List[str],
        brand_name: str
    ) -> List[str]:
        """
        STAGE 2: Recherche web structurée pour trouver des compétiteurs
        
        Returns:
            Liste d'URLs trouvées via recherche
        """
        logger.info("🔎 Stage 2: Web search for competitors...")
        
        # Générer requêtes de recherche
        search_queries = self._generate_search_queries(
            primary_industry=primary_industry,
            sub_industry=sub_industry,
            offerings=offerings,
            brand_name=brand_name
        )
        
        all_urls = set()
        
        for query in search_queries[:4]:  # Max 4 requêtes pour limiter
            logger.info(f"  🔍 Query: {query}")
            
            try:
                urls = self._search_google(query, max_results=10)
                all_urls.update(urls)
                logger.info(f"    → Found {len(urls)} URLs")
                
                # Délai entre requêtes
                time.sleep(self.search_delay)
                
            except Exception as e:
                logger.warning(f"    ⚠️  Search failed: {e}")
                continue
        
        urls_list = list(all_urls)
        logger.info(f"📦 Stage 2 total: {len(urls_list)} unique URLs from web search")
        return urls_list
    
    def _generate_search_queries(
        self,
        primary_industry: str,
        sub_industry: str,
        offerings: List[str],
        brand_name: str
    ) -> List[str]:
        """
        Génère des requêtes de recherche intelligentes orientées "trouver des compétiteurs"
        
        Returns:
            Liste de requêtes (français + anglais pour Québec/Canada)
        """
        queries = []
        
        # Utiliser sub_industry si disponible, sinon primary
        industry = (sub_industry if sub_industry else primary_industry).lower()
        
        # Traductions FR pour industrie
        industry_fr = self._translate_industry_to_french(industry)
        
        # Query 1: Alternative à [brand]
        if brand_name:
            queries.append(f"alternative à {brand_name} Québec")
            queries.append(f"{brand_name} competitors Canada")
        
        # Query 2: Meilleurs [type de service]
        if industry_fr:
            queries.append(f"meilleures compagnies {industry_fr} Québec")
        if industry:
            queries.append(f"top {industry} companies Quebec Canada")
        
        # Query 3: [Offering] + location
        if offerings:
            main_offering = offerings[0].lower()
            queries.append(f"{main_offering} Québec Canada")
        
        # Query 4: [Industry] concurrents
        if industry:
            queries.append(f"{industry} leaders Canada")
        
        return queries
    
    def _translate_industry_to_french(self, industry: str) -> str:
        """
        Traduit industrie en français naturel
        """
        translations = {
            'insurance': "d'assurance",
            'life insurance': 'assurance vie',
            'financial services': 'services financiers',
            'banking': 'bancaires',
            'real estate': 'immobilier',
            'technology': 'technologie',
            'software': 'logiciels',
            'consulting': 'consultation',
            'legal': 'juridiques',
            'accounting': 'comptables'
        }
        
        industry_lower = industry.lower()
        for en, fr in translations.items():
            if en in industry_lower:
                return fr
        
        return industry
    
    def _search_google(self, query: str, max_results: int = 10) -> List[str]:
        """
        Effectue une recherche web et extrait les URLs des résultats organiques
        Essaie Google d'abord, puis DuckDuckGo en fallback
        
        Args:
            query: Requête de recherche
            max_results: Nombre max de résultats à extraire
            
        Returns:
            Liste d'URLs extraites
        """
        # Essayer Google d'abord
        urls = self._try_google_search(query, max_results)
        
        # Si Google échoue, essayer DuckDuckGo
        if not urls:
            logger.debug(f"Google failed, trying DuckDuckGo for: {query}")
            urls = self._try_duckduckgo_search(query, max_results)
        
        return urls
    
    def _try_google_search(self, query: str, max_results: int = 10) -> List[str]:
        """Essaie une recherche Google"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"
            
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(search_url, headers=headers, timeout=self.search_timeout)
            response.raise_for_status()
            
            # Vérifier si Google a bloqué (CAPTCHA)
            if 'captcha' in response.text.lower() or response.status_code == 429:
                logger.debug("Google CAPTCHA detected")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = self._parse_google_results(soup)
            
            return urls
            
        except Exception as e:
            logger.debug(f"Google search error: {e}")
            return []
    
    def _try_duckduckgo_search(self, query: str, max_results: int = 10) -> List[str]:
        """Essaie une recherche DuckDuckGo (fallback)"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            
            response = requests.get(search_url, headers=headers, timeout=self.search_timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = self._parse_duckduckgo_results(soup)
            
            return urls[:max_results]
            
        except Exception as e:
            logger.debug(f"DuckDuckGo search error: {e}")
            return []
    
    def _parse_google_results(self, soup: BeautifulSoup) -> List[str]:
        """
        Parse la page Google et extrait les URLs des résultats organiques
        """
        urls = []
        
        # Méthode 1: Chercher tous les liens <a>
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Format Google: /url?q=https://example.com&sa=...
            if '/url?q=' in href:
                try:
                    # Extraire l'URL réelle
                    url = href.split('/url?q=')[1].split('&')[0]
                    
                    # Valider que c'est une vraie URL
                    if url.startswith('http') and self._is_valid_competitor_url(url):
                        urls.append(url)
                except:
                    continue
            
            # Format direct
            elif href.startswith('http') and self._is_valid_competitor_url(href):
                urls.append(href)
        
        # Dédupliquer
        unique_urls = list(dict.fromkeys(urls))  # Garde l'ordre
        
        return unique_urls
    
    def _parse_duckduckgo_results(self, soup: BeautifulSoup) -> List[str]:
        """
        Parse la page DuckDuckGo et extrait les URLs des résultats organiques
        """
        urls = []
        
        # DuckDuckGo utilise des balises avec class="result__url"
        for result in soup.find_all('a', class_='result__url'):
            href = result.get('href', '')
            
            if href.startswith('http') and self._is_valid_competitor_url(href):
                urls.append(href)
        
        # Fallback: chercher dans les liens directs
        if not urls:
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Format DuckDuckGo: //duckduckgo.com/l/?uddg=https://example.com
                if 'uddg=' in href:
                    try:
                        url = href.split('uddg=')[1].split('&')[0]
                        from urllib.parse import unquote
                        url = unquote(url)
                        
                        if url.startswith('http') and self._is_valid_competitor_url(url):
                            urls.append(url)
                    except:
                        continue
        
        # Dédupliquer
        unique_urls = list(dict.fromkeys(urls))
        
        return unique_urls
    
    def _is_valid_competitor_url(self, url: str) -> bool:
        """
        Filtre les URLs non pertinentes (social media, directories, etc.)
        """
        from utils.competitor_extractor import CompetitorExtractor
        
        domain = CompetitorExtractor._extract_domain(url)
        if not domain:
            return False
        
        # Utiliser la liste d'exclusion de CompetitorExtractor
        if CompetitorExtractor._is_excluded_domain(domain):
            return False
        
        return True
    
    def _validate_and_score_competitors(
        self,
        urls: List[str],
        our_url: str,
        primary_industry: str,
        offerings: List[str],
        url_sources: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        STAGE 3: Valide existence, analyse contenu, calcule score de pertinence
        
        Args:
            urls: Liste d'URLs candidates
            our_url: Notre URL
            primary_industry: Industrie
            offerings: Liste d'offerings
            url_sources: Dict {url: 'llm'|'web_search'|'both'}
            
        Returns:
            Liste de dicts avec score, type, reason
        """
        logger.info(f"🎯 Stage 3: Validating and scoring {len(urls)} candidates...")
        
        scored = []
        
        # Extraire mots-clés de notre industrie/offerings pour comparaison
        our_keywords = self._extract_keywords(primary_industry, offerings)
        
        for url in urls:
            try:
                logger.info(f"  🔍 Validating: {url}")
                
                # 1. Valider existence (DNS + HTTP)
                if not self._check_url_exists(url):
                    logger.info(f"  ❌ {url}: URL does not exist or not reachable")
                    continue
                
                # 2. Analyser le contenu de la page d'accueil
                competitor_data = self._analyze_competitor_homepage(url)
                if not competitor_data:
                    logger.info(f"  ⚠️  {url}: Could not analyze homepage")
                    continue
                
                logger.info(f"  ✅ {url}: Homepage analyzed successfully")
                
                # 3. Calculer score de pertinence
                score = self._calculate_relevance_score(
                    competitor_data=competitor_data,
                    our_keywords=our_keywords,
                    primary_industry=primary_industry,
                    offerings=offerings,
                    source=url_sources.get(url, 'web_search')
                )
                
                # 4. Classifier direct/indirect
                comp_type = 'direct' if score >= self.threshold_direct else 'indirect'
                
                # Filtrer si score trop faible
                if score < self.threshold_indirect:
                    logger.debug(f"  🔻 {url}: score {score:.2f} too low")
                    continue
                
                # 5. Générer justification
                reason = self._generate_reason(
                    competitor_data=competitor_data,
                    score=score,
                    comp_type=comp_type,
                    primary_industry=primary_industry
                )
                
                from utils.competitor_extractor import CompetitorExtractor
                domain = CompetitorExtractor._extract_domain(url)
                
                scored.append({
                    'domain': domain,
                    'homepage_url': url,
                    'score': round(score, 2),
                    'type': comp_type,
                    'reason': reason,
                    'source': url_sources.get(url, 'web_search')
                })
                
                logger.info(f"  ✅ {domain}: {score:.2f} ({comp_type}) - {reason[:50]}...")
                
            except Exception as e:
                logger.debug(f"  ⚠️  {url}: Validation error - {e}")
                continue
        
        logger.info(f"📊 Stage 3 complete: {len(scored)} validated competitors")
        return scored
    
    def _check_url_exists(self, url: str) -> bool:
        """
        Vérifie qu'une URL existe et est accessible
        1. DNS lookup
        2. HEAD request rapide
        """
        try:
            # 1. Vérifier DNS
            parsed = urlparse(url)
            domain = parsed.netloc
            socket.gethostbyname(domain)
            
            # 2. HEAD request
            response = requests.head(
                url,
                timeout=self.validation_timeout,
                allow_redirects=True,
                headers={'User-Agent': self.user_agent}
            )
            
            # Accepter 200-399
            is_valid = response.status_code < 400
            if not is_valid:
                logger.debug(f"  ❌ URL check failed: HTTP {response.status_code} for {url}")
            return is_valid
            
        except socket.gaierror as e:
            logger.debug(f"  ❌ DNS lookup failed for {url}: {e}")
            return False
        except requests.exceptions.Timeout:
            logger.debug(f"  ⏱️  Timeout checking {url}")
            return False
        except requests.exceptions.RequestException as e:
            logger.debug(f"  ❌ HTTP request failed for {url}: {e}")
            return False
        except Exception as e:
            logger.debug(f"  ❌ URL validation error for {url}: {e}")
            return False
    
    def _analyze_competitor_homepage(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Analyse la page d'accueil d'un compétiteur
        Extrait: title, meta description, h1, h2, keywords
        """
        try:
            response = requests.get(
                url,
                timeout=self.validation_timeout,
                headers={'User-Agent': self.user_agent}
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire éléments clés
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            
            meta_desc = soup.find('meta', {'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ''
            
            h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
            h2_tags = [h.get_text().strip() for h in soup.find_all('h2')][:5]
            
            # Combiner tout le texte pour extraction de mots-clés
            all_text = ' '.join([title_text, description] + h1_tags + h2_tags)
            
            # Extraire mots-clés
            keywords = self._extract_keywords_from_text(all_text)
            
            return {
                'title': title_text,
                'description': description,
                'h1': h1_tags,
                'h2': h2_tags,
                'keywords': keywords
            }
            
        except Exception as e:
            logger.debug(f"Homepage analysis failed for {url}: {e}")
            return None
    
    def _extract_keywords(self, industry: str, offerings: List[str]) -> Set[str]:
        """
        Extrait mots-clés depuis industrie et offerings
        """
        keywords = set()
        
        # Industry
        if industry:
            keywords.update(industry.lower().split())
        
        # Offerings
        for offering in offerings:
            if offering:
                keywords.update(str(offering).lower().split())
        
        # Retirer stop words français/anglais communs
        stop_words = {'le', 'la', 'les', 'de', 'des', 'un', 'une', 'et', 'ou',
                     'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'for'}
        keywords = {k for k in keywords if len(k) > 2 and k not in stop_words}
        
        return keywords
    
    def _extract_keywords_from_text(self, text: str) -> Set[str]:
        """
        Extrait mots-clés d'un texte
        """
        if not text:
            return set()
        
        # Tokenizer simple
        words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿæœç]{3,}\b', text.lower())
        
        # Stop words
        stop_words = {'le', 'la', 'les', 'de', 'des', 'un', 'une', 'et', 'ou', 'pour', 'dans', 'sur',
                     'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in', 'for', 'with', 'on', 'at'}
        
        keywords = set([w for w in words if w not in stop_words])
        
        return keywords
    
    def _calculate_relevance_score(
        self,
        competitor_data: Dict[str, Any],
        our_keywords: Set[str],
        primary_industry: str,
        offerings: List[str],
        source: str
    ) -> float:
        """
        Calcule le score de pertinence (0-1) d'un compétiteur
        
        Basé sur:
        - Recouvrement de mots-clés
        - Présence industrie dans texte
        - Présence offerings
        - Bonus si trouvé dans LLM ET web search
        """
        score = 0.0
        
        competitor_keywords = competitor_data.get('keywords', set())
        
        # 1. Recouvrement de mots-clés (max 0.5)
        if our_keywords and competitor_keywords:
            overlap = len(our_keywords & competitor_keywords)
            total = len(our_keywords | competitor_keywords)
            jaccard = overlap / total if total > 0 else 0
            score += jaccard * 0.5
        
        # 2. Industrie mentionnée (0.2)
        all_text = ' '.join([
            competitor_data.get('title', ''),
            competitor_data.get('description', ''),
            ' '.join(competitor_data.get('h1', [])),
            ' '.join(competitor_data.get('h2', []))
        ]).lower()
        
        if primary_industry.lower() in all_text:
            score += 0.2
        
        # 3. Offerings mentionnés (0.15)
        for offering in offerings[:2]:
            if str(offering).lower() in all_text:
                score += 0.075
        
        # 4. Bonus source (0.15)
        if source == 'both':  # Trouvé dans LLM ET web
            score += 0.15
        elif source == 'llm':  # LLM seulement
            score += 0.05
        
        return min(score, 1.0)
    
    def _generate_reason(self, competitor_data: Dict, score: float, comp_type: str, primary_industry: str) -> str:
        """
        Génère une justification courte en français
        """
        reasons = []
        
        # Industrie
        title = competitor_data.get('title', '')
        if primary_industry.lower() in title.lower():
            reasons.append(f"Même secteur ({primary_industry})")
        
        # Type
        if comp_type == 'direct':
            reasons.append("Concurrent direct")
        else:
            reasons.append("Concurrent indirect")
        
        # Score
        if score >= 0.7:
            reasons.append("Forte similarité")
        elif score >= 0.5:
            reasons.append("Similarité moyenne")
        
        return ', '.join(reasons) if reasons else f"Score: {score:.2f}"


# Instance globale
competitor_discovery = CompetitorDiscovery()
