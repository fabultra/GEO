"""
Module 3: Competitive Intelligence Active
Reverse-engineer exactement pourquoi les compétiteurs apparaissent dans les LLMs
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

class CompetitiveIntelligence:
    """Analyse détaillée des compétiteurs"""
    
    def analyze_competitors(self, competitors_urls: List[str], visibility_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse approfondie des compétiteurs qui apparaissent dans les LLMs
        
        Args:
            competitors_urls: URLs des compétiteurs à analyser
            visibility_data: Données de visibilité avec mentions des compétiteurs
        
        Returns:
            Analyse détaillée avec actions concrètes
        """
        analyses = []
        
        for comp_url in competitors_urls[:3]:  # Top 3 compétiteurs
            logger.info(f"Analyzing competitor: {comp_url}")
            
            try:
                analysis = self.analyze_single_competitor(comp_url, visibility_data)
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze {comp_url}: {str(e)}")
                continue
        
        return {
            "competitors_analyzed": len(analyses),
            "analyses": analyses,
            "comparative_metrics": self.generate_comparative_table(analyses),
            "actionable_insights": self.generate_actionable_insights(analyses)
        }
    
    def analyze_single_competitor(self, comp_url: str, visibility_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse un compétiteur en profondeur"""
        
        # Fetch la page principale
        try:
            response = requests.get(comp_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; GEOBot/1.0)'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraire métriques
            metrics = {
                "url": comp_url,
                "domain": comp_url.split('//')[1].split('/')[0],
                "word_count": len(soup.get_text().split()),
                "h1_count": len(soup.find_all('h1')),
                "h2_count": len(soup.find_all('h2')),
                "h3_count": len(soup.find_all('h3')),
                "has_tldr": bool(soup.find(string=lambda text: text and ('TL;DR' in text or 'En bref' in text))),
                "lists_count": len(soup.find_all(['ul', 'ol'])),
                "tables_count": len(soup.find_all('table')),
                "has_faq": bool(soup.find(string=lambda text: text and 'FAQ' in text)),
                "schema_count": len(soup.find_all('script', {'type': 'application/ld+json'})),
                "meta_description": soup.find('meta', {'name': 'description'}).get('content', '') if soup.find('meta', {'name': 'description'}) else '',
                "images_with_alt": len([img for img in soup.find_all('img') if img.get('alt')])
            }
            
            # Statistiques dans le contenu
            text_content = soup.get_text()
            metrics['stats_count'] = text_content.count('%') + text_content.count('$') + text_content.count(' millions')
            
            # Calculer visibilité LLM
            comp_domain = metrics['domain']
            llm_visibility = self.calculate_competitor_visibility(comp_domain, visibility_data)
            metrics['llm_visibility'] = llm_visibility
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing {comp_url}: {str(e)}")
            return {"url": comp_url, "error": str(e)}
    
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
    
    def generate_comparative_table(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Génère un tableau comparatif"""
        if not analyses:
            return {}
        
        # Utiliser les vrais noms des compétiteurs (domaines)
        headers = ["Métrique"]
        for analysis in analyses[:3]:
            domain = analysis.get('domain', 'Compétiteur')
            # Raccourcir si trop long
            if len(domain) > 25:
                domain = domain[:22] + '...'
            headers.append(domain)
        headers.extend(["NOUS", "GAP"])
        
        table = {
            "headers": headers,
            "rows": []
        }
        
        metrics_to_compare = [
            ("Longueur (mots)", "word_count"),
            ("Statistiques", "stats_count"),
            ("H2 descriptifs", "h2_count"),
            ("TL;DR", "has_tldr"),
            ("Listes", "lists_count"),
            ("Tableaux", "tables_count"),
            ("FAQ", "has_faq"),
            ("Schema markup", "schema_count")
        ]
        
        for metric_name, metric_key in metrics_to_compare:
            row = [metric_name]
            values = []
            
            for analysis in analyses[:3]:
                value = analysis.get(metric_key, 0)
                row.append(str(value))
                values.append(value if isinstance(value, (int, float)) else 0)
            
            # Ajouter "NOUS" (supposons 0 pour l'instant)
            row.append("0")
            
            # Calculer GAP
            avg_competitors = sum(values) / len(values) if values else 0
            gap = f"-{avg_competitors:.0f}"
            row.append(gap)
            
            table["rows"].append(row)
        
        return table
    
    def generate_actionable_insights(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Génère des insights actionnables"""
        insights = []
        
        if not analyses:
            return insights
        
        # Insight 1: Longueur de contenu
        avg_words = sum([a.get('word_count', 0) for a in analyses]) / len(analyses)
        if avg_words > 2000:
            insights.append({
                "priority": "HAUTE",
                "title": "Augmenter la longueur du contenu",
                "problem": f"Les compétiteurs ont en moyenne {avg_words:.0f} mots par page",
                "action": f"Passer nos pages de ~800 mots à {avg_words:.0f} mots minimum",
                "impact": "Visibilité LLM +30-40%",
                "time": "2-3 heures par page"
            })
        
        # Insight 2: TL;DR
        tldr_count = sum([1 for a in analyses if a.get('has_tldr')])
        if tldr_count >= 2:
            insights.append({
                "priority": "CRITIQUE",
                "title": "Ajouter TL;DR en début de page",
                "problem": f"{tldr_count}/{len(analyses)} compétiteurs ont un TL;DR",
                "action": "Ajouter un résumé de 40-60 mots au début de chaque page principale",
                "impact": "Visibilité ChatGPT +25%",
                "time": "15 minutes par page"
            })
        
        # Insight 3: Statistiques
        avg_stats = sum([a.get('stats_count', 0) for a in analyses]) / len(analyses)
        if avg_stats > 5:
            insights.append({
                "priority": "HAUTE",
                "title": "Augmenter la densité de statistiques",
                "problem": f"Compétiteurs ont en moyenne {avg_stats:.0f} stats par page",
                "action": "Ajouter 10-15 statistiques par page avec sources",
                "impact": "Crédibilité +40%, Visibilité +20%",
                "time": "1 heure de recherche par page"
            })
        
        # Insight 4: Schema markup
        avg_schema = sum([a.get('schema_count', 0) for a in analyses]) / len(analyses)
        if avg_schema > 0:
            insights.append({
                "priority": "HAUTE",
                "title": "Implémenter Schema markup",
                "problem": f"Compétiteurs ont en moyenne {avg_schema:.1f} schemas par page",
                "action": "Ajouter Organization, FAQPage, LocalBusiness schemas",
                "impact": "Indexation LLM +50%",
                "time": "30 minutes par page"
            })
        
        return insights
