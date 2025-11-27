"""
Utilitaire pour extraire et normaliser les URLs des compétiteurs
Version 2 - Complète et robuste, sans code incomplet
"""
import re
import logging
from typing import List, Set, Dict, Any, Optional
from urllib.parse import urlparse, urlunparse
import json

logger = logging.getLogger(__name__)


class CompetitorExtractor:
    """
    Extraction intelligente des compétiteurs depuis différentes sources
    Pipeline Stage 1 : Extraction depuis visibilité/LLM
    """
    
    # Domaines à exclure systématiquement
    EXCLUDED_DOMAINS = {
        # Social media
        'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
        'youtube.com', 'tiktok.com', 'pinterest.com',
        # Search engines
        'google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com',
        # Directories/Annuaires
        'yelp.com', 'pagesjaunes.ca', 'yellowpages.com', 'tripadvisor.com',
        'bbb.org', 'crunchbase.com',
        # Job boards
        'indeed.com', 'glassdoor.com', 'monster.com', 'linkedin.com/jobs',
        # Marketplaces génériques
        'amazon.com', 'ebay.com', 'etsy.com', 'alibaba.com',
        # Wikis/Encyclopedias
        'wikipedia.org', 'wikihow.com', 'quora.com', 'reddit.com',
        # News génériques
        'cnn.com', 'bbc.com', 'nytimes.com', 'forbes.com',
        # Gov/Edu
        '.gov', '.edu', '.gc.ca'
    }
    
    @staticmethod
    def extract_from_visibility_results(
        visibility_data: Dict[str, Any], 
        max_competitors: int = 20
    ) -> List[str]:
        """
        Extrait les URLs des compétiteurs depuis les résultats de visibilité/LLM
        
        Stage 1 du pipeline : collecte brute depuis les réponses IA
        
        Args:
            visibility_data: Données de visibilité contenant réponses ChatGPT/Claude/etc
            max_competitors: Nombre maximum de candidats à retourner
            
        Returns:
            Liste d'URLs normalisées et dédupliquées (domaines uniques)
        """
        if not visibility_data:
            logger.warning("No visibility data provided")
            return []
        
        competitor_domains = set()
        competitor_urls = []
        
        # Méthode 1: Format 'details' (ancien format)
        visibility_details = visibility_data.get('details', [])
        for detail in visibility_details:
            answer = detail.get('answer', '')
            urls = CompetitorExtractor._extract_urls_from_text(answer)
            
            for url in urls:
                normalized_url = CompetitorExtractor._normalize_url(url)
                if not normalized_url:
                    continue
                    
                domain = CompetitorExtractor._extract_domain(normalized_url)
                if domain and domain not in competitor_domains:
                    if not CompetitorExtractor._is_excluded_domain(domain):
                        competitor_domains.add(domain)
                        competitor_urls.append(normalized_url)
        
        # Méthode 2: Format 'queries' (nouveau format)
        queries_data = visibility_data.get('queries', [])
        for query_data in queries_data:
            platforms = query_data.get('platforms', {})
            
            for platform_name, platform_data in platforms.items():
                # Extraire depuis full_response
                full_response = platform_data.get('full_response', '')
                urls = CompetitorExtractor._extract_urls_from_text(full_response)
                
                for url in urls:
                    normalized_url = CompetitorExtractor._normalize_url(url)
                    if not normalized_url:
                        continue
                    
                    domain = CompetitorExtractor._extract_domain(normalized_url)
                    if domain and domain not in competitor_domains:
                        if not CompetitorExtractor._is_excluded_domain(domain):
                            competitor_domains.add(domain)
                            competitor_urls.append(normalized_url)
                
                # Extraire depuis competitors_mentioned si disponible
                competitors_mentioned = platform_data.get('competitors_mentioned', [])
                for comp in competitors_mentioned:
                    if isinstance(comp, dict):
                        comp_urls = comp.get('urls', [])
                        for url in comp_urls:
                            normalized_url = CompetitorExtractor._normalize_url(url)
                            if not normalized_url:
                                continue
                            
                            domain = CompetitorExtractor._extract_domain(normalized_url)
                            if domain and domain not in competitor_domains:
                                if not CompetitorExtractor._is_excluded_domain(domain):
                                    competitor_domains.add(domain)
                                    competitor_urls.append(normalized_url)
        
        # Dédupliquer et trier pour déterminisme
        unique_urls = sorted(list(set(competitor_urls)))[:max_competitors]
        
        logger.info(f"📊 Stage 1: Extracted {len(unique_urls)} candidate URLs from visibility data")
        return unique_urls
    
    @staticmethod
    def _extract_urls_from_text(text: str) -> List[str]:
        """
        Extrait toutes les URLs d'un texte avec regex robuste
        
        Args:
            text: Texte contenant potentiellement des URLs
            
        Returns:
            Liste d'URLs brutes extraites
        """
        if not text or not isinstance(text, str):
            return []
        
        # Pattern pour URLs complètes
        url_pattern = r'https?://[^\s<>"\'()]+(?:[^\s<>"\'(),.;!?])'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Pattern pour domaines www sans protocole
        www_pattern = r'www\.[a-zA-Z0-9][-a-zA-Z0-9]*\.[-a-zA-Z0-9.]+[a-zA-Z]'
        www_domains = re.findall(www_pattern, text, re.IGNORECASE)
        
        all_urls = urls + [f'https://{d}' for d in www_domains]
        
        return all_urls
    
    @staticmethod
    def _normalize_url(url: str) -> Optional[str]:
        """
        Normalise une URL (schéma, domaine, path)
        
        Args:
            url: URL brute ou domaine
            
        Returns:
            URL normalisée ou None si invalide
        """
        if not url or not isinstance(url, str):
            return None
        
        url = url.strip()
        
        # Retirer trailing slashes et fragments
        url = url.rstrip('/').split('#')[0].split('?')[0]
        
        # Ajouter https:// si manquant
        if not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                url = 'https:' + url
            else:
                url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            
            # Valider qu'il y a bien un domaine
            if not parsed.netloc:
                return None
            
            # Reconstruire proprement (normalise le schéma en https)
            normalized = urlunparse((
                'https',  # Force https
                parsed.netloc,
                parsed.path or '/',
                '',  # params
                '',  # query
                ''   # fragment
            ))
            
            return normalized
            
        except Exception as e:
            logger.debug(f"Failed to normalize URL {url}: {e}")
            return None
    
    @staticmethod
    def _extract_domain(url: str) -> Optional[str]:
        """
        Extrait le domaine normalisé d'une URL
        Supprime www. pour uniformiser
        
        Args:
            url: URL complète
            
        Returns:
            Domaine normalisé (sans www., en minuscules) ou None
        """
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Supprimer www. pour uniformiser
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain if domain else None
            
        except Exception as e:
            logger.debug(f"Failed to extract domain from {url}: {e}")
            return None
    
    @staticmethod
    def _normalize_domain(url_or_domain: str) -> Optional[str]:
        """
        Alias de _extract_domain pour compatibilité
        """
        # Si c'est déjà juste un domaine
        if '://' not in url_or_domain and '/' not in url_or_domain:
            domain = url_or_domain.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        
        # Sinon traiter comme URL
        return CompetitorExtractor._extract_domain(url_or_domain)
    
    @staticmethod
    def _is_excluded_domain(domain: str) -> bool:
        """
        Vérifie si un domaine doit être exclu (directories, social, etc.)
        
        Args:
            domain: Domaine à vérifier
            
        Returns:
            True si domaine à exclure
        """
        if not domain:
            return True
        
        domain_lower = domain.lower()
        
        # Check exact match
        if domain_lower in CompetitorExtractor.EXCLUDED_DOMAINS:
            return True
        
        # Check suffix match (pour .gov, .edu, etc.)
        for excluded in CompetitorExtractor.EXCLUDED_DOMAINS:
            if excluded.startswith('.') and domain_lower.endswith(excluded):
                return True
        
        # Check substring match pour domaines complexes
        for excluded in CompetitorExtractor.EXCLUDED_DOMAINS:
            if not excluded.startswith('.') and excluded in domain_lower:
                return True
        
        return False
    
    @staticmethod
    def filter_self_domain(urls: List[str], own_url: str) -> List[str]:
        """
        Filtre les URLs qui pointent vers notre propre domaine
        
        Args:
            urls: Liste d'URLs à filtrer
            own_url: Notre URL ou domaine
            
        Returns:
            Liste filtrée sans notre domaine
        """
        own_domain = CompetitorExtractor._extract_domain(own_url)
        if not own_domain:
            logger.warning(f"Could not extract own domain from {own_url}")
            return urls
        
        filtered = []
        for url in urls:
            url_domain = CompetitorExtractor._extract_domain(url)
            if url_domain and url_domain != own_domain:
                filtered.append(url)
            else:
                logger.debug(f"Filtered self domain: {url}")
        
        logger.info(f"🔍 Filtered {len(urls) - len(filtered)} self-domain URLs")
        return filtered
    
    @staticmethod
    async def suggest_competitors_with_claude(
        industry: str, 
        company_type: str,
        anthropic_client,
        max_competitors: int = 5
    ) -> List[str]:
        """
        Fallback: suggère des compétiteurs via Claude
        
        Args:
            industry: Industrie principale
            company_type: Type d'entreprise
            anthropic_client: Client Anthropic
            max_competitors: Nombre de compétiteurs
            
        Returns:
            Liste d'URLs suggérées par Claude
        """
        try:
            from config import CLAUDE_MODEL
            
            prompt = f"""Suggère {max_competitors} URLs RÉELLES de sites web de compétiteurs directs pour une entreprise de type "{company_type}" dans l'industrie "{industry}" au Québec/Canada.

IMPORTANT : 
- URLs de compétiteurs RÉELS qui existent vraiment
- Mix francophones québécois ET anglophones canadiens
- Pas de hallucinations

Réponds UNIQUEMENT avec un JSON valide:
{{
  "competitors": ["https://competitor1.com", "https://competitor2.com", ...]
}}"""
            
            response = anthropic_client.messages.create(
                model=CLAUDE_MODEL,
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
            
            result = json.loads(response_text.strip())
            competitors = result.get('competitors', [])[:max_competitors]
            
            # Valider et normaliser
            validated = []
            for url in competitors:
                normalized = CompetitorExtractor._normalize_url(url)
                if normalized:
                    validated.append(normalized)
            
            logger.info(f"✅ Claude suggested {len(validated)} competitors")
            return validated
            
        except Exception as e:
            logger.error(f"Failed to get competitor suggestions from Claude: {e}")
            return []
