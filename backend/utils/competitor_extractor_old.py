"""
Utilitaire pour extraire et normaliser les URLs des compétiteurs
Élimine la duplication de code dans server.py
"""
import re
import logging
from typing import List, Set, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class CompetitorExtractor:
    """Extraction intelligente des compétiteurs depuis différentes sources"""
    
    @staticmethod
    def extract_from_visibility_results(visibility_data: Dict[str, Any], 
                                       max_competitors: int = 5) -> List[str]:
        """
        Extrait les URLs des compétiteurs depuis les résultats de visibilité
        
        Args:
            visibility_data: Données de visibilité contenant les réponses IA
            max_competitors: Nombre maximum de compétiteurs à retourner
            
        Returns:
            Liste d'URLs normalisées et dédupliquées
        """
        competitor_urls = []
        competitor_domains = set()
        
        # Récupérer les détails de visibilité
        visibility_details = visibility_data.get('details', [])
        queries_data = visibility_data.get('queries', [])
        
        # Méthode 1: Extraire depuis 'details' (format ancien)
        for detail in visibility_details:
            answer = detail.get('answer', '')
            urls = CompetitorExtractor._extract_urls_from_text(answer)
            
            for url in urls:
                domain = CompetitorExtractor._normalize_domain(url)
                if domain and domain not in competitor_domains:
                    competitor_domains.add(domain)
                    competitor_urls.append(CompetitorExtractor._normalize_url(url))
        
        # Méthode 2: Extraire depuis 'queries' (format nouveau)
        for query_data in queries_data:
            platforms = query_data.get('platforms', {})
            
            for platform, platform_data in platforms.items():
                full_response = platform_data.get('full_response', '')
                urls = CompetitorExtractor._extract_urls_from_text(full_response)
                
                for url in urls:
                    domain = CompetitorExtractor._normalize_domain(url)
                    if domain and domain not in competitor_domains:
                        competitor_domains.add(domain)
                        competitor_urls.append(CompetitorExtractor._normalize_url(url))
        
        # Trier pour déterminisme et limiter
        competitor_urls = sorted(list(set(competitor_urls)))[:max_competitors]
        
        logger.info(f"📊 Extracted {len(competitor_urls)} unique competitor URLs")
        return competitor_urls
    
    @staticmethod
    def _extract_urls_from_text(text: str) -> List[str]:
        """Extrait toutes les URLs d'un texte"""
        if not text:
            return []
        
        # Pattern pour URLs complètes et domaines
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, text)
        
        return urls
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalise une URL"""
        if not url:
            return ""
        
        # Ajouter https:// si manquant
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        return url
    
    @staticmethod
    def _normalize_domain(url: str) -> str:
        """
        Extrait et normalise le domaine d'une URL
        Supprime www. pour éviter les doublons
        """
        if not url:
            return ""
        
        try:
            # Normaliser l'URL d'abord
            url = CompetitorExtractor._normalize_url(url)
            
            # Extraire le domaine
            if '//' in url:
                domain = url.split('//')[1].split('/')[0]
            else:
                domain = url.split('/')[0]
            
            # Supprimer www. pour uniformiser
            domain = domain.replace('www.', '').lower()
            
            return domain
        except Exception as e:
            logger.warning(f"Failed to normalize domain for {url}: {e}")
            return ""
    
    @staticmethod
    async def suggest_competitors_with_claude(industry: str, 
                                             company_type: str,
                                             anthropic_client,
                                             max_competitors: int = 5) -> List[str]:
        """
        Suggère des compétiteurs via Claude basé sur l'industrie
        
        Args:
            industry: Industrie principale
            company_type: Type d'entreprise
            anthropic_client: Client Anthropic
            max_competitors: Nombre de compétiteurs à suggérer
            
        Returns:
            Liste d'URLs suggérées
        """
        try:
            from config import CLAUDE_MODEL
            import json
            
            prompt = f"""Suggère {max_competitors} URLs de sites web compétiteurs directs pour une entreprise de type "{company_type}" dans l'industrie "{industry}".

Réponds UNIQUEMENT avec un JSON valide:
{{
  "competitors": ["https://competitor1.com", "https://competitor2.com", ...]
}}"""
            
            response = anthropic_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=500,
                temperature=0,  # Déterministe
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
            
            logger.info(f"✅ Claude suggested {len(competitors)} competitors")
            return competitors
            
        except Exception as e:
            logger.error(f"Failed to get competitor suggestions from Claude: {e}")
            return []
    
    @staticmethod
    def filter_self_domain(urls: List[str], own_domain: str) -> List[str]:
        """
        Filtre les URLs qui pointent vers notre propre domaine
        
        Args:
            urls: Liste d'URLs à filtrer
            own_domain: Notre propre domaine
            
        Returns:
            Liste filtrée sans notre domaine
        """
        own_domain_normalized = CompetitorExtractor._normalize_domain(own_domain)
        
        filtered = []
        for url in urls:
            domain = CompetitorExtractor._normalize_domain(url)
            if domain and domain != own_domain_normalized:
                filtered.append(url)
        
        return filtered
