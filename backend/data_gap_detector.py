"""Détecte le manque de données chiffrées critiques pour les IA"""
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

INDUSTRY_THRESHOLDS = {
    'finance': 15, 'insurance': 10, 'real_estate': 12,
    'technology': 8, 'healthcare': 10, 'professional_services': 8,
    'ecommerce': 12, 'saas': 10, 'manufacturing': 10, 'default': 5
}

class DataGapDetector:
    def analyze_data_gaps(self, crawl_data: Dict[str, Any], industry: str = 'default') -> Dict[str, Any]:
        threshold = INDUSTRY_THRESHOLDS.get(industry, 5)
        pages_analysis = []
        total_stats = 0
        
        for page in crawl_data.get('pages', []):
            content = ' '.join(page.get('paragraphs', []))
            stats_found = self._count_stats(content)
            total_stats += stats_found
            
            pages_analysis.append({
                'url': page.get('url', ''),
                'stats_found': stats_found,
                'expected': threshold,
                'gap_score': min(10, (stats_found / threshold) * 10) if threshold > 0 else 0,
                'missing_stats': max(0, threshold - stats_found)
            })
        
        expected_total = threshold * len(crawl_data.get('pages', []))
        has_gap = total_stats < expected_total
        
        return {
            'global_stats': {
                'total_stats_found': total_stats,
                'expected_minimum': expected_total,
                'has_data_gap': has_gap,
                'gap_severity': self._get_severity(total_stats, expected_total),
                'pages_analyzed': len(pages_analysis)
            },
            'by_page': sorted(pages_analysis, key=lambda x: x['gap_score'])[:5],
            'recommendations': self._generate_recs(pages_analysis, threshold, industry)
        }
    
    def _count_stats(self, text: str) -> int:
        percentages = len(re.findall(r'\d+(?:\.\d+)?%', text))
        currency = len(re.findall(r'\$[\d,]+', text))
        numbers = len(re.findall(r'\b\d{1,3}(?:,\d{3})+\b', text))
        dates = len(re.findall(r'\b20\d{2}\b', text))
        return percentages + currency + numbers + dates
    
    def _get_severity(self, found: int, expected: int) -> str:
        ratio = found / expected if expected > 0 else 0
        if ratio < 0.3:
            return 'CRITICAL'
        if ratio < 0.6:
            return 'HIGH'
        if ratio < 0.8:
            return 'MEDIUM'
        return 'LOW'
    
    def _generate_recs(self, pages: List[Dict], threshold: int, industry: str) -> List[Dict]:
        examples = {
            'finance': ['Market size: "$X billion AUM"', 'Performance: "8.5% annual return"'],
            'insurance': ['Coverage: "$1M-$5M limits"', 'Claims: "95% paid in 30 days"'],
            'real_estate': ['Sales: "127 properties sold in 2024"', 'Price: "Median $542K"'],
            'default': ['Add market data', 'Include customer metrics']
        }
        
        recs = []
        for page in sorted(pages, key=lambda x: x['stats_found'])[:3]:
            if page['stats_found'] < threshold:
                recs.append({
                    'page': page['url'],
                    'priority': 'CRITICAL' if page['stats_found'] == 0 else 'HIGH',
                    'action': f"Add {page['missing_stats']} statistics",
                    'examples': examples.get(industry, examples['default']),
                    'estimated_impact': '+15% AI citation' if page['missing_stats'] > 5 else '+8% AI citation'
                })
        return recs
