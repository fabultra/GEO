"""
Analyse GEO du budget de tokens et risque de troncature pour les moteurs génératifs.
Estime la consommation de tokens par page et identifie les risques de troncature dans les LLMs.
La densité informationnelle est une métrique technique, PAS un score de qualité GEO.
"""
import re
import logging
from typing import Dict, Any, List

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not installed - using approximation")

logger = logging.getLogger(__name__)

class TokenAnalyzer:
    """
    Analyse le budget de tokens pour moteurs génératifs (ChatGPT, Claude, etc.).
    Identifie les pages à risque de troncature et mesure la densité informationnelle.
    
    IMPORTANT GEO: La densité n'est PAS un indicateur de qualité. Ce qui compte:
    - Éviter la troncature des pages clés
    - Structurer le contenu pour extraction facile par IA
    - Placer l'info critique en début de page
    """
    def __init__(self):
        self.encoder = tiktoken.encoding_for_model("gpt-4") if TIKTOKEN_AVAILABLE else None
    
    def analyze_token_budget(self, crawl_data: Dict[str, Any], token_limit: int = 8000) -> Dict[str, Any]:
        """
        Analyse GEO du budget de tokens par page et identification des risques de troncature.
        Retourne truncation_risk avec risk_level (HIGH/MEDIUM/LOW) et density_explanation.
        """
        pages_analysis = []
        total_tokens = 0
        pages_truncate = 0
        
        for page in crawl_data.get('pages', []):
            analysis = self._analyze_page(page, token_limit)
            pages_analysis.append(analysis)
            total_tokens += analysis['tokens']
            if analysis['will_truncate']:
                pages_truncate += 1
        
        avg_tokens = total_tokens / len(pages_analysis) if pages_analysis else 0
        avg_density = sum(p['info_density'] for p in pages_analysis) / len(pages_analysis) if pages_analysis else 0
        
        # Calcul du risk_level pour truncation
        if pages_truncate >= 3:
            risk_level = "HIGH"
        elif pages_truncate in (1, 2):
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'global_analysis': {
                'total_tokens': total_tokens,
                'avg_tokens_per_page': round(avg_tokens, 0),
                'pages_will_truncate': pages_truncate,
                'info_density_avg': round(avg_density, 4),
                'density_rating': self._rate_density(avg_density),
                'truncation_risk': {
                    'token_limit': token_limit,
                    'pages_will_truncate': pages_truncate,
                    'risk_level': risk_level
                },
                'density_explanation': "La densité informationnelle mesure le nombre de faits par rapport au volume de texte. Ce n'est PAS une note de performance GEO. En GEO, le plus important est que les contenus critiques ne soient pas tronqués et restent facilement exploitables par les moteurs génératifs."
            },
            'by_page': sorted(pages_analysis, key=lambda x: -x['tokens'])[:5],
            'recommendations': self._generate_recs(pages_analysis, token_limit)
        }
    
    def _analyze_page(self, page: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Analyse une page: tokens, densité informationnelle, risque troncature pour LLMs."""
        content = page.get('title', '') + ' ' + page.get('meta_description', '') + ' '
        content += ' '.join(page.get('paragraphs', []))
        
        tokens = self._estimate_tokens(content)
        facts = self._count_facts(content)
        density = facts / tokens if tokens > 0 else 0
        
        return {
            'url': page.get('url', ''),
            'tokens': tokens,
            'will_truncate': tokens > limit,
            'tokens_lost': max(0, tokens - limit),
            'info_density': round(density, 4),
            'density_rating': self._rate_density(density),
            'facts_found': facts
        }
    
    def _estimate_tokens(self, text: str) -> int:
        if self.encoder:
            return len(self.encoder.encode(text))
        return int(len(text.split()) * 1.3)
    
    def _count_facts(self, text: str) -> int:
        facts = len(re.findall(r'\d+(?:\.\d+)?%|\$[\d,]+|\b\d{1,3}(?:,\d{3})+\b|\b20\d{2}\b', text))
        facts += len(re.findall(r'(?<!\. )[A-Z][a-z]+', text))
        action_verbs = ['permet', 'offre', 'garantit', 'assure', 'fournit', 'crée', 'génère']
        facts += sum(text.lower().count(v) for v in action_verbs)
        return facts
    
    def _rate_density(self, density: float) -> str:
        """
        Labellise la densité informationnelle (faits/tokens) de façon descriptive.
        IMPORTANT GEO: Ce n'est PAS un score de qualité, juste un indicateur technique.
        """
        if density >= 0.030:
            return 'DENSITÉ TRÈS ÉLEVÉE'
        if density >= 0.020:
            return 'DENSITÉ ÉLEVÉE'
        if density >= 0.010:
            return 'DENSITÉ MOYENNE'
        return 'DENSITÉ FAIBLE'
    
    def _generate_recs(self, pages: List[Dict], limit: int) -> List[Dict]:
        recs = []
        for page in pages:
            if page['will_truncate']:
                recs.append({
                    'page': page['url'],
                    'priority': 'CRITICAL',
                    'issue': f"Page will be truncated ({page['tokens']} > {limit})",
                    'action': f"Reduce by {page['tokens_lost']} tokens (~{page['tokens_lost']//1.3:.0f} words)",
                    'how_to': ['Remove repetition', 'Use bullet points', 'Move details to subpages'],
                    'estimated_impact': 'Prevent info loss in AI responses'
                })
            elif page['info_density'] < 0.010:
                recs.append({
                    'page': page['url'],
                    'priority': 'HIGH',
                    'issue': f"Low density ({page['info_density']:.4f})",
                    'action': f"Add {30 - page['facts_found']} concrete facts",
                    'how_to': ['Add stats/dates', 'Replace vague language', 'Include numbers'],
                    'estimated_impact': '+12% AI citation chance'
                })
        return recs[:5]
