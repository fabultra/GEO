"""
Service de crawling de sites web
Extrait le contenu structuré pour l'analyse GEO
"""
import asyncio
import logging
from typing import Dict, Any, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import json

from config import (
    MAX_PAGES_TO_CRAWL,
    CRAWL_DELAY_SECONDS,
    CRAWL_TIMEOUT_SECONDS,
    USER_AGENT
)

logger = logging.getLogger(__name__)


class WebCrawler:
    """Crawle un site web et extrait le contenu structuré"""
    
    def __init__(self):
        self.max_pages = MAX_PAGES_TO_CRAWL
        self.delay = CRAWL_DELAY_SECONDS
        self.timeout = CRAWL_TIMEOUT_SECONDS
        self.user_agent = USER_AGENT
    
    async def crawl_website(self, url: str) -> Dict[str, Any]:
        """
        Crawle un site web et retourne le contenu structuré
        
        Args:
            url: URL du site à crawler
            
        Returns:
            Dictionnaire contenant les données crawlées
        """
        try:
            logger.info(f"Starting crawl for {url}")
            
            # Normaliser l'URL
            url = self._normalize_url(url)
            
            parsed_url = urlparse(url)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            visited = set()
            to_visit = [url]
            pages_data = []
            
            while to_visit and len(visited) < self.max_pages:
                current_url = to_visit.pop(0)
                
                if current_url in visited:
                    continue
                    
                visited.add(current_url)
                
                try:
                    # Crawler la page
                    page_data = await self._crawl_page(current_url, base_domain, to_visit, visited)
                    
                    if page_data:
                        pages_data.append(page_data)
                        logger.info(f"Crawled: {current_url}")
                    
                    # Être poli avec le serveur
                    await asyncio.sleep(self.delay)
                    
                except Exception as e:
                    logger.warning(f"Failed to crawl {current_url}: {str(e)}")
                    continue
            
            return {
                'base_url': url,
                'pages_crawled': len(pages_data),
                'pages': pages_data
            }
            
        except Exception as e:
            logger.error(f"Crawl error: {str(e)}")
            raise
    
    async def _crawl_page(self, url: str, base_domain: str, 
                         to_visit: List[str], visited: set) -> Dict[str, Any]:
        """Crawle une page individuelle"""
        response = requests.get(
            url, 
            timeout=self.timeout, 
            headers={'User-Agent': self.user_agent}
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extraire le contenu
        page_data = self._extract_page_content(soup, url)
        
        # Extraire les liens internes
        self._extract_internal_links(soup, url, base_domain, to_visit, visited)
        
        return page_data
    
    def _extract_page_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extrait le contenu structuré d'une page"""
        # Title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        meta_description = meta_desc.get('content', '') if meta_desc else ""
        
        # Headings
        h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
        h2_tags = [h.get_text().strip() for h in soup.find_all('h2')]
        h3_tags = [h.get_text().strip() for h in soup.find_all('h3')]
        
        # Paragraphs (filtrer les courts)
        paragraphs = [
            p.get_text().strip() 
            for p in soup.find_all('p') 
            if len(p.get_text().strip()) > 50
        ]
        
        # JSON-LD
        json_ld = []
        for script in soup.find_all('script', {'type': 'application/ld+json'}):
            try:
                json_ld.append(json.loads(script.string))
            except:
                pass
        
        # Word count
        word_count = sum(len(p.split()) for p in paragraphs)
        
        return {
            'url': url,
            'title': title_text,
            'meta_description': meta_description,
            'h1': h1_tags,
            'h2': h2_tags,
            'h3': h3_tags,
            'paragraphs': paragraphs[:10],  # Garder les 10 premiers
            'json_ld': json_ld,
            'word_count': word_count
        }
    
    def _extract_internal_links(self, soup: BeautifulSoup, current_url: str,
                                base_domain: str, to_visit: List[str], 
                                visited: set):
        """Extrait les liens internes pour continuer le crawl"""
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            absolute_url = urljoin(current_url, href)
            
            # Vérifier que c'est un lien interne valide
            if (absolute_url.startswith(base_domain) and 
                absolute_url not in visited and 
                len(to_visit) < 20 and
                self._is_valid_link(absolute_url)):
                to_visit.append(absolute_url)
    
    def _is_valid_link(self, url: str) -> bool:
        """Vérifie si un lien est valide pour le crawl"""
        # Éviter les fichiers non-HTML et les ancres
        invalid_patterns = [
            '#', 'javascript:', 'mailto:', 
            '.pdf', '.jpg', '.png', '.gif', 
            '.zip', '.doc', '.xls'
        ]
        
        url_lower = url.lower()
        return not any(pattern in url_lower for pattern in invalid_patterns)
    
    def _normalize_url(self, url: str) -> str:
        """Normalise une URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
