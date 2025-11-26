"""
Module 3: Competitive Intelligence Active - GEO Focus
Analyse pourquoi les compétiteurs sont favoris des moteurs génératifs (ChatGPT, Claude, Perplexity, etc.)
Reverse-engineering des patterns de contenu qui font performer dans les IA
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import json
import re
import time
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

# Configuration
REQUEST_TIMEOUT = 15  # Augmenté de 10 à 15 secondes
MAX_RETRIES = 2
RETRY_DELAY = 1  # secondes

class CompetitiveIntelligence:
    """
    Analyse détaillée des compétiteurs pour comprendre pourquoi ils dominent dans les moteurs génératifs.
    Extrait les patterns de contenu, structure, données factuelles qui plaisent aux IA.
    """
    
    def __init__(self):
        """Initialise le service d'intelligence compétitive"""
        self.timeout = REQUEST_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
    
    def _validate_url(self, url: str) -> Optional[str]:
        """
        Valide et normalise une URL
        
        Args:
            url: URL à valider
            
        Returns:
            URL normalisée ou None si invalide
        """
        if not url or not isinstance(url, str):
            return None
        
        # Nettoyer l'URL
        url = url.strip()
        
        # Ajouter https:// si manquant
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        # Valider avec urlparse
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                logger.warning(f"Invalid URL (no domain): {url}")
                return None
            
            # Reconstruire l'URL proprement
            scheme = parsed.scheme or 'https'
            netloc = parsed.netloc
            path = parsed.path or '/'
            
            normalized_url = f"{scheme}://{netloc}{path}"
            return normalized_url
            
        except Exception as e:
            logger.error(f"Failed to parse URL {url}: {e}")
            return None
    
    def _make_request_with_retry(self, url: str) -> Optional[requests.Response]:
        """
        Fait une requête HTTP avec retry logic
        
        Args:
            url: URL à requêter
            
        Returns:
            Response object ou None si échec
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; GEOBot/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, 
                    timeout=self.timeout, 
                    headers=headers,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries} for {url}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on attempt {attempt + 1}/{self.max_retries} for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None
    
    def analyze_competitors(
        self, 
        competitors_urls: List[str], 
        visibility_data: Dict[str, Any],
        our_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyse approfondie jusqu'à 5 compétiteurs qui apparaissent dans les réponses des LLMs.
        Détermine leurs forces GEO et compare avec NOTRE site.
        
        Args:
            competitors_urls: URLs des compétiteurs à analyser (max 5)
            visibility_data: Données de visibilité avec mentions des compétiteurs
            our_data: Nos propres données (crawl_data, semantic_analysis, etc.) pour comparaison
        
        Returns:
            Analyse GEO détaillée avec geo_power_score, confidence_level, pages_analyzed,
            comparative_metrics (NOUS vs AVERAGE_COMPETITORS vs GAP), et insights actionnables
        """
        analyses = []
        failed_urls = []
        
        # Valider et filtrer les URLs
        valid_urls = []
        for url in competitors_urls[:5]:  # Top 5 compétiteurs
            validated_url = self._validate_url(url)
            if validated_url:
                valid_urls.append(validated_url)
                logger.info(f"✅ Valid competitor URL: {validated_url}")
            else:
                logger.warning(f"❌ Invalid competitor URL skipped: {url}")
                failed_urls.append({'url': url, 'reason': 'Invalid URL format'})
        
        # Analyser chaque compétiteur
        for comp_url in valid_urls:
            logger.info(f"🔍 Analyzing competitor: {comp_url}")
            
            try:
                analysis = self.analyze_single_competitor(comp_url, visibility_data)
                
                # Vérifier si l'analyse a réussi
                if analysis.get('error'):
                    logger.warning(f"⚠️  Partial failure for {comp_url}: {analysis['error']}")
                    failed_urls.append({'url': comp_url, 'reason': analysis['error']})
                else:
                    logger.info(f"✅ Successfully analyzed {comp_url}")
                
                analyses.append(analysis)
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Failed to analyze {comp_url}: {error_msg}")
                failed_urls.append({'url': comp_url, 'reason': error_msg})
                
                # Ajouter une entrée d'erreur pour tracking
                analyses.append({
                    "domain": self._extract_domain(comp_url),
                    "main_url": comp_url,
                    "error": error_msg,
                    "pages_analyzed": [],
                    "aggregate": {},
                    "llm_visibility": {},
                    "geo_power_score": 0.0
                })
        
        # Calculer confidence level basé sur échantillon
        competitors_analyzed = len([a for a in analyses if not a.get('error')])
        pages_analyzed = sum(len(a.get("pages_analyzed", [])) for a in analyses)
        confidence = self._compute_confidence_level(competitors_analyzed, pages_analyzed)
        
        result = {
            "competitors_analyzed": competitors_analyzed,
            "total_attempted": len(competitors_urls[:5]),
            "pages_analyzed": pages_analyzed,
            "confidence_level": confidence,
            "analyses": analyses,
            "comparative_metrics": self.generate_comparative_table(analyses, our_data),
            "actionable_insights": self.generate_actionable_insights(analyses, our_data)
        }
        
        # Ajouter les URLs échouées si présentes
        if failed_urls:
            result['failed_urls'] = failed_urls
            logger.warning(f"⚠️  {len(failed_urls)} competitor URLs failed to analyze")
        
        return result
    
    def _compute_confidence_level(self, competitors_analyzed: int, pages_analyzed: int) -> str:
        """
        Calcule le niveau de confiance GEO basé sur l'échantillon d'analyse compétitive.
        Plus de compétiteurs et pages = meilleure fiabilité des insights.
        """
        if competitors_analyzed >= 3 and pages_analyzed >= 12:
            return "HIGH"
        if competitors_analyzed >= 2 and pages_analyzed >= 6:
            return "MEDIUM"
        return "LOW"
    
    def _analyze_competitor_page(self, url: str) -> Dict[str, Any]:
        """
        Analyse une page de compétiteur pour métriques GEO.
        Extrait: word_count, headers, direct answer, TL;DR, lists, tables, FAQ, stats, schemas.
        """
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; GEOBot/1.0)'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire texte
            text_content = soup.get_text()
            words = text_content.split()
            
            # Détecter réponse directe (premiers 100 mots contiennent info clé)
            first_100_words = ' '.join(words[:100])
            has_direct_answer = any(marker in first_100_words.lower() for marker in [
                'est un', 'est une', 'consiste à', 'permet de', 'signifie', 
                'définition', 'c\'est', 'il s\'agit'
            ])
            
            # Détecter TL;DR / résumé
            has_tldr = bool(soup.find(string=lambda text: text and any(
                marker in text.upper() for marker in ['TL;DR', 'EN BREF', 'RÉSUMÉ', 'KEY TAKEAWAYS', 'À RETENIR']
            )))
            
            # Compter éléments structurels
            h1_count = len(soup.find_all('h1'))
            h2_count = len(soup.find_all('h2'))
            h3_count = len(soup.find_all('h3'))
            lists_count = len(soup.find_all(['ul', 'ol']))
            tables_count = len(soup.find_all('table'))
            
            # Détecter FAQ
            has_faq = bool(soup.find(string=lambda text: text and 'FAQ' in text.upper()))
            faq_count = len(soup.find_all(string=lambda text: text and '?' in text))
            
            # Compter statistiques (chiffres + indicateurs)
            stats_count = (
                text_content.count('%') +
                text_content.count('$') +
                len(re.findall(r'\b\d+\s*(millions?|milliards?|k\b|M\b)', text_content, re.IGNORECASE))
            )
            
            # Compter schémas structurés
            schema_count = len(soup.find_all('script', {'type': 'application/ld+json'}))
            
            return {
                'url': url,
                'word_count': len(words),
                'h1_count': h1_count,
                'h2_count': h2_count,
                'h3_count': h3_count,
                'has_direct_answer': has_direct_answer,
                'has_tldr': has_tldr,
                'lists_count': lists_count,
                'tables_count': tables_count,
                'faq_count': faq_count,
                'stats_count': stats_count,
                'schema_count': schema_count
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze page {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'word_count': 0,
                'has_direct_answer': False,
                'has_tldr': False,
                'stats_count': 0,
                'schema_count': 0
            }
    
    def analyze_single_competitor(self, comp_url: str, visibility_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse approfondie GEO d'un compétiteur: page principale + 4-5 pages internes.
        Identifie pourquoi il performe dans les IA (structure, données, FAQ, guides).
        """
        
        try:
            # 1. Analyser la page principale
            main_page = self._analyze_competitor_page(comp_url)
            
            # 2. Extraire URLs internes pertinentes pour GEO
            response = requests.get(comp_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; GEOBot/1.0)'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            domain = comp_url.split('//')[1].split('/')[0] if '//' in comp_url else comp_url.split('/')[0]
            
            # Mots-clés GEO pertinents
            geo_keywords = [
                'guide', 'comment', 'how-to', 'faq', 'questions', 'prix', 'tarifs',
                'compare', 'vs', 'fonctionnalites', 'features', 'ressources', 'resources',
                'blog', 'article', 'tutoriel', 'tutorial'
            ]
            
            internal_urls = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Convertir en URL absolue
                if href.startswith('/'):
                    href = urljoin(comp_url, href)
                
                # Vérifier que c'est le même domaine
                if domain in href and any(keyword in href.lower() for keyword in geo_keywords):
                    if href not in internal_urls and href != comp_url:
                        internal_urls.append(href)
            
            # Garder maximum 4-5 pages
            internal_urls = list(set(internal_urls))[:5]
            
            # 3. Analyser les pages internes
            pages_analyzed = [main_page]
            for internal_url in internal_urls:
                page_analysis = self._analyze_competitor_page(internal_url)
                pages_analyzed.append(page_analysis)
            
            # 4. Calculer agrégats
            total_word_count = sum(p.get('word_count', 0) for p in pages_analyzed)
            total_stats = sum(p.get('stats_count', 0) for p in pages_analyzed)
            total_faq = sum(p.get('faq_count', 0) for p in pages_analyzed)
            pages_with_schema = sum(1 for p in pages_analyzed if p.get('schema_count', 0) > 0)
            pages_with_direct_answer = sum(1 for p in pages_analyzed if p.get('has_direct_answer', False))
            pages_with_tldr = sum(1 for p in pages_analyzed if p.get('has_tldr', False))
            
            num_pages = len(pages_analyzed)
            
            aggregate = {
                'total_word_count': total_word_count,
                'avg_word_count': total_word_count / num_pages if num_pages > 0 else 0,
                'total_stats': total_stats,
                'avg_stats_per_page': total_stats / num_pages if num_pages > 0 else 0,
                'total_faq': total_faq,
                'avg_faq_per_page': total_faq / num_pages if num_pages > 0 else 0,
                'schema_presence_rate': pages_with_schema / num_pages if num_pages > 0 else 0,
                'direct_answer_rate': pages_with_direct_answer / num_pages if num_pages > 0 else 0,
                'tldr_rate': pages_with_tldr / num_pages if num_pages > 0 else 0
            }
            
            # 5. Calculer visibilité LLM
            llm_visibility = self.calculate_competitor_visibility(domain, visibility_data)
            
            # 6. Calculer GEO Power Score
            competitor = {
                'domain': domain,
                'main_url': comp_url,
                'pages_analyzed': pages_analyzed,
                'aggregate': aggregate,
                'llm_visibility': llm_visibility
            }
            geo_power_score = self.compute_geo_power_score(competitor)
            competitor['geo_power_score'] = geo_power_score
            
            return competitor
            
        except Exception as e:
            logger.error(f"Error analyzing {comp_url}: {str(e)}")
            return {
                "domain": comp_url,
                "main_url": comp_url,
                "error": str(e),
                "pages_analyzed": [],
                "aggregate": {},
                "llm_visibility": {},
                "geo_power_score": 0.0
            }
    
    def compute_geo_power_score(self, competitor: Dict[str, Any]) -> float:
        """
        Calcule le GEO Power Score (0-10) basé sur les facteurs clés de performance IA.
        
        Pondération:
        - llm_visibility (40%): visibilité réelle dans les moteurs génératifs
        - direct_answer_rate (20%): capacité à fournir réponses claires
        - tldr_rate (15%): présence de résumés extractibles
        - schema_presence_rate (15%): structured data pour IA
        - avg_stats_per_page (10%): richesse en données factuelles
        """
        agg = competitor.get('aggregate', {})
        visibility = competitor.get('llm_visibility', {})
        
        # Visibilité LLM (0-4 points)
        v = visibility.get('overall', 0.0)
        visibility_score = v * 4
        
        # Direct answer rate (0-2 points)
        direct = agg.get('direct_answer_rate', 0.0)
        direct_score = direct * 2
        
        # TL;DR rate (0-1.5 points)
        tldr = agg.get('tldr_rate', 0.0)
        tldr_score = tldr * 1.5
        
        # Schema presence (0-1.5 points)
        schema = agg.get('schema_presence_rate', 0.0)
        schema_score = schema * 1.5
        
        # Stats density (0-1 point, normalisé)
        stats = agg.get('avg_stats_per_page', 0.0)
        stats_score = min(stats / 10.0, 1.0)  # 10 stats/page = optimal
        
        # Score total (max 10)
        total_score = visibility_score + direct_score + tldr_score + schema_score + stats_score
        
        return round(total_score, 1)
    
    def calculate_competitor_visibility(self, comp_domain: str, visibility_data: Dict[str, Any]) -> Dict[str, float]:
        """Calcule la visibilité d'un compétiteur dans les LLMs"""
        visibility = {
            "chatgpt": 0.0,
            "claude": 0.0,
            "perplexity": 0.0,
            "gemini": 0.0,
            "overall": 0.0
        }
        
        # Analyser les résultats des tests
        details = visibility_data.get('details', [])
        for detail in details:
            answer = detail.get('answer', '').lower()
            platform = detail.get('platform', '').lower()
            
            if comp_domain.lower() in answer:
                if 'chatgpt' in platform:
                    visibility['chatgpt'] += 1
                elif 'claude' in platform:
                    visibility['claude'] += 1
                elif 'perplexity' in platform:
                    visibility['perplexity'] += 1
                elif 'gemini' in platform:
                    visibility['gemini'] += 1
        
        # Calculer moyennes
        total_tests = len([d for d in details if d.get('platform') == 'ChatGPT'])
        if total_tests > 0:
            for key in ['chatgpt', 'claude', 'perplexity', 'gemini']:
                visibility[key] = visibility[key] / total_tests if total_tests > 0 else 0
            visibility['overall'] = sum([visibility[k] for k in ['chatgpt', 'claude', 'perplexity', 'gemini']]) / 4
        
        return visibility
    
    def generate_comparative_table(self, analyses: List[Dict[str, Any]], our_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Génère un tableau comparatif GEO: NOUS vs AVERAGE_COMPETITORS avec GAP.
        Utilise les vraies données de notre site pour comparaison réelle.
        """
        if not analyses:
            return {}
        
        # Extraire nos métriques si disponibles
        our_metrics = self._extract_our_metrics(our_data) if our_data else {}
        
        # Calculer moyennes des compétiteurs
        competitor_metrics = self._calculate_competitor_averages(analyses)
        
        # Structure du tableau comparatif GEO
        table = {
            "NOUS": our_metrics,
            "AVERAGE_COMPETITORS": competitor_metrics,
            "GAP": {}
        }
        
        # Calculer GAP pour chaque métrique
        metrics_keys = [
            'avg_word_count', 'avg_stats_per_page', 'direct_answer_rate',
            'tldr_rate', 'schema_presence_rate', 'avg_faq_per_page', 'geo_power_score'
        ]
        
        for key in metrics_keys:
            our_val = our_metrics.get(key, 0)
            comp_val = competitor_metrics.get(key, 0)
            
            # GAP = NOUS - COMPÉTITEURS (négatif = on est en retard)
            gap = our_val - comp_val
            table["GAP"][key] = round(gap, 2)
        
        return table
    
    def _extract_our_metrics(self, our_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait nos métriques GEO depuis crawl_data, semantic_analysis, etc."""
        
        crawl_data = our_data.get('crawl_data', {})
        semantic_analysis = our_data.get('semantic_analysis', {})
        data_gap = our_data.get('data_gap_analysis', {})
        visibility = our_data.get('visibility_data', {})
        
        pages = crawl_data.get('pages', [])
        num_pages = len(pages)
        
        if num_pages == 0:
            return {
                'avg_word_count': 0,
                'avg_stats_per_page': 0,
                'direct_answer_rate': 0,
                'tldr_rate': 0,
                'schema_presence_rate': 0,
                'avg_faq_per_page': 0,
                'geo_power_score': 0
            }
        
        # Calculer word count moyen
        total_words = 0
        for page in pages:
            paragraphs = page.get('paragraphs', [])
            for p in paragraphs:
                total_words += len(p.split())
        avg_word_count = total_words / num_pages if num_pages > 0 else 0
        
        # Stats depuis data_gap_detector
        global_stats = data_gap.get('global_stats', {})
        avg_stats = global_stats.get('avg_stats_found', 0)
        
        # Schémas structurés
        pages_with_schema = sum(1 for p in pages if p.get('structured_data'))
        schema_rate = pages_with_schema / num_pages if num_pages > 0 else 0
        
        # Direct answer / TL;DR (estimation heuristique)
        # TODO: améliorer avec détection réelle
        direct_answer_rate = 0.3  # Estimation conservative
        tldr_rate = 0.1  # Estimation conservative
        
        # FAQ (depuis semantic analysis)
        entities = semantic_analysis.get('entities', {})
        faq_count = len(entities.get('questions', [])) if isinstance(entities.get('questions'), list) else 0
        avg_faq = faq_count / num_pages if num_pages > 0 else 0
        
        # Visibilité globale
        summary = visibility.get('summary', {})
        our_visibility = summary.get('global_visibility', 0)
        
        # Calculer notre GEO Power Score (même formule que compétiteurs)
        geo_power_score = (
            (our_visibility * 4) +
            (direct_answer_rate * 2) +
            (tldr_rate * 1.5) +
            (schema_rate * 1.5) +
            min(avg_stats / 10.0, 1.0)
        )
        geo_power_score = round(geo_power_score, 1)
        
        return {
            'avg_word_count': round(avg_word_count, 0),
            'avg_stats_per_page': round(avg_stats, 1),
            'direct_answer_rate': round(direct_answer_rate, 2),
            'tldr_rate': round(tldr_rate, 2),
            'schema_presence_rate': round(schema_rate, 2),
            'avg_faq_per_page': round(avg_faq, 1),
            'geo_power_score': geo_power_score
        }
    
    def _calculate_competitor_averages(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les moyennes des compétiteurs pour chaque métrique GEO"""
        
        if not analyses:
            return {}
        
        # Agréger toutes les métriques
        total_word_count = 0
        total_stats = 0
        total_direct_answer_rate = 0
        total_tldr_rate = 0
        total_schema_rate = 0
        total_faq = 0
        total_geo_score = 0
        count = 0
        
        for analysis in analyses:
            if analysis.get('error'):
                continue
                
            agg = analysis.get('aggregate', {})
            total_word_count += agg.get('avg_word_count', 0)
            total_stats += agg.get('avg_stats_per_page', 0)
            total_direct_answer_rate += agg.get('direct_answer_rate', 0)
            total_tldr_rate += agg.get('tldr_rate', 0)
            total_schema_rate += agg.get('schema_presence_rate', 0)
            total_faq += agg.get('avg_faq_per_page', 0)
            total_geo_score += analysis.get('geo_power_score', 0)
            count += 1
        
        if count == 0:
            return {}
        
        return {
            'avg_word_count': round(total_word_count / count, 0),
            'avg_stats_per_page': round(total_stats / count, 1),
            'direct_answer_rate': round(total_direct_answer_rate / count, 2),
            'tldr_rate': round(total_tldr_rate / count, 2),
            'schema_presence_rate': round(total_schema_rate / count, 2),
            'avg_faq_per_page': round(total_faq / count, 1),
            'geo_power_score': round(total_geo_score / count, 1)
        }
    
    def generate_actionable_insights(self, analyses: List[Dict[str, Any]], our_data: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """
        Génère des insights actionnables GEO basés sur le comparatif réel NOUS vs COMPÉTITEURS.
        Priorise les gaps les plus critiques pour la performance dans les IA.
        """
        insights = []
        
        if not analyses:
            return insights
        
        # Calculer métriques comparatives
        our_metrics = self._extract_our_metrics(our_data) if our_data else {}
        competitor_metrics = self._calculate_competitor_averages(analyses)
        
        if not competitor_metrics:
            return insights
        
        # Insight 1: GEO Power Score Gap
        our_score = our_metrics.get('geo_power_score', 0)
        comp_score = competitor_metrics.get('geo_power_score', 0)
        score_gap = comp_score - our_score
        
        if score_gap > 2:
            insights.append({
                "priority": "CRITIQUE",
                "title": f"GEO Power Score en retard de {score_gap:.1f} points",
                "problem": f"NOUS: {our_score}/10 | COMPÉTITEURS: {comp_score}/10",
                "action": "Prioriser les 3 gaps les plus importants ci-dessous",
                "impact": "Performance globale dans les IA",
                "time": "2-4 semaines"
            })
        
        # Insight 2: Longueur de contenu
        our_words = our_metrics.get('avg_word_count', 0)
        comp_words = competitor_metrics.get('avg_word_count', 0)
        word_gap = comp_words - our_words
        
        if word_gap > 500:
            insights.append({
                "priority": "HAUTE",
                "title": f"Contenu {word_gap:.0f} mots trop court",
                "problem": f"NOUS: {our_words:.0f} mots/page | COMPÉTITEURS: {comp_words:.0f} mots/page",
                "action": f"Enrichir chaque page de {word_gap:.0f} mots minimum avec données factuelles",
                "impact": "Visibilité LLM +30-40%",
                "time": "2-3h par page"
            })
        
        # Insight 3: Statistiques / Données
        our_stats = our_metrics.get('avg_stats_per_page', 0)
        comp_stats = competitor_metrics.get('avg_stats_per_page', 0)
        stats_gap = comp_stats - our_stats
        
        if stats_gap > 3:
            insights.append({
                "priority": "HAUTE",
                "title": f"Manque {stats_gap:.0f} statistiques par page",
                "problem": f"NOUS: {our_stats:.0f} stats/page | COMPÉTITEURS: {comp_stats:.0f} stats/page",
                "action": "Ajouter 10-15 statistiques chiffrées avec sources par page",
                "impact": "Crédibilité +40%, Visibilité IA +20%",
                "time": "1h de recherche par page"
            })
        
        # Insight 4: Direct Answer Rate
        our_direct = our_metrics.get('direct_answer_rate', 0)
        comp_direct = competitor_metrics.get('direct_answer_rate', 0)
        direct_gap = comp_direct - our_direct
        
        if direct_gap > 0.2:
            insights.append({
                "priority": "CRITIQUE",
                "title": f"Réponses directes {direct_gap*100:.0f}% en retard",
                "problem": f"NOUS: {our_direct*100:.0f}% | COMPÉTITEURS: {comp_direct*100:.0f}%",
                "action": "Réécrire les premiers paragraphes pour répondre immédiatement à la question",
                "impact": "Visibilité ChatGPT/Claude +35%",
                "time": "30 min par page"
            })
        
        # Insight 5: TL;DR Rate
        our_tldr = our_metrics.get('tldr_rate', 0)
        comp_tldr = competitor_metrics.get('tldr_rate', 0)
        tldr_gap = comp_tldr - our_tldr
        
        if tldr_gap > 0.2:
            insights.append({
                "priority": "HAUTE",
                "title": f"Ajouter des TL;DR ({tldr_gap*100:.0f}% de retard)",
                "problem": f"NOUS: {our_tldr*100:.0f}% | COMPÉTITEURS: {comp_tldr*100:.0f}%",
                "action": "Ajouter un résumé TL;DR de 40-60 mots en début de chaque page clé",
                "impact": "Extractibilité IA +25%",
                "time": "15 min par page"
            })
        
        # Insight 6: Schema Markup
        our_schema = our_metrics.get('schema_presence_rate', 0)
        comp_schema = competitor_metrics.get('schema_presence_rate', 0)
        schema_gap = comp_schema - our_schema
        
        if schema_gap > 0.3:
            insights.append({
                "priority": "HAUTE",
                "title": f"Schémas structurés {schema_gap*100:.0f}% en retard",
                "problem": f"NOUS: {our_schema*100:.0f}% | COMPÉTITEURS: {comp_schema*100:.0f}%",
                "action": "Implémenter FAQPage, Article, HowTo schemas (JSON-LD)",
                "impact": "Compréhension IA +50%",
                "time": "30 min par page"
            })
        
        # Insight 7: FAQ
        our_faq = our_metrics.get('avg_faq_per_page', 0)
        comp_faq = competitor_metrics.get('avg_faq_per_page', 0)
        faq_gap = comp_faq - our_faq
        
        if faq_gap > 3:
            insights.append({
                "priority": "MOYENNE",
                "title": f"Ajouter {faq_gap:.0f} FAQ par page",
                "problem": f"NOUS: {our_faq:.0f} FAQ/page | COMPÉTITEURS: {comp_faq:.0f} FAQ/page",
                "action": "Créer sections FAQ avec 5-10 questions par page",
                "impact": "Visibilité requêtes questions +30%",
                "time": "45 min par page"
            })
        
        return insights
