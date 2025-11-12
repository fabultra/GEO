"""
Module 2: Génération automatique de contenu GEO-optimisé
"""
import asyncio
import logging
from typing import List, Dict, Any
from anthropic import AsyncAnthropic
import os

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Génère automatiquement 10 articles GEO-optimisés"""
    
    def __init__(self):
        self.claude_client = AsyncAnthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    
    async def generate_articles(self, opportunities: List[Dict[str, Any]], site_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère 10 articles GEO-optimisés basés sur les opportunités
        
        Args:
            opportunities: Top 10 opportunités identifiées (requêtes à 0% visibilité)
            site_context: Contexte du site (industrie, expertise, etc.)
        
        Returns:
            Liste de 10 articles générés
        """
        articles = []
        
        for i, opp in enumerate(opportunities[:10], 1):
            logger.info(f"Generating article {i}/10: {opp['query']}")
            
            try:
                article = await self.generate_single_article(opp, site_context)
                articles.append(article)
                
                # Petit délai pour éviter rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to generate article {i}: {str(e)}")
                continue
        
        return articles
    
    async def generate_single_article(self, opportunity: Dict[str, Any], site_context: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un article GEO-optimisé complet"""
        
        query = opportunity['query']
        competitors_content = opportunity.get('competitors_content', '')
        
        prompt = f"""
Vous êtes un expert rédacteur GEO spécialisé en contenu optimisé pour les IA génératives.

CONTEXTE DU SITE:
- Industrie: {site_context.get('industry', 'assurance')}
- Nom: {site_context.get('site_name', 'SEKOIA')}
- URL: {site_context.get('url', '')}
- Expertise: {site_context.get('expertise', 'Courtage en assurance depuis 1915')}

REQUÊTE CIBLE: "{query}"

OBJECTIF: Créer un article GEO-optimisé de 2500-3000 mots qui sera parfaitement cité par ChatGPT, Claude, Perplexity.

STRUCTURE OBLIGATOIRE (respecter exactement):

# [Titre H1 optimisé - max 60 caractères - incluant année 2025]

## TL;DR (40-60 mots MAXIMUM)
[Réponse directe avec 2 statistiques clés]

## Introduction (150-200 mots)
[Contexte + importance + ce que le lecteur va apprendre]

## Section 1: [H2 principal répondant à la question]
[300-400 mots avec 3-4 statistiques]

### Sous-section 1.1 [H3]
[200-250 mots]

> **💡 À retenir:**
> [Citation box avec fait clé]

### Sous-section 1.2 [H3]
[200-250 mots]

**Tableau comparatif:**
[Créer un tableau pertinent avec 3-4 colonnes]

## Section 2: [H2 complémentaire]
[300-400 mots avec 3-4 statistiques]

[Répéter structure...]

## Section 3: [H2 complémentaire]
[300-400 mots]

## FAQ
[5-7 questions avec réponses courtes et factuelles]

## Conclusion
[100-150 mots avec call-to-action]

## Sources
[Lister 8-12 sources avec URLs]

CONTRAINTES QUALITÉ:
- Minimum 15 statistiques avec sources
- 3-5 citation boxes
- 2-3 tableaux
- 5-7 questions FAQ
- Ton professionnel mais accessible
- Perspective {site_context.get('site_name', 'experte')}
- Aucun contenu marketing lourd

Générez l'article complet maintenant en Markdown.
"""
        
        response = await self.claude_client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=8000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        
        article_content = response.content[0].text
        
        # Générer le schema markup
        schema_json = self.generate_article_schema(query, article_content, site_context)
        
        return {
            "title": query.title(),
            "query": query,
            "content_markdown": article_content,
            "content_html": self.markdown_to_html(article_content),
            "schema_markup": schema_json,
            "word_count": len(article_content.split()),
            "stats_count": article_content.count('%') + article_content.count('$'),  # Approximation
            "geo_score_estimate": self.estimate_geo_score(article_content)
        }
    
    def markdown_to_html(self, markdown_content: str) -> str:
        """Convertit Markdown en HTML (simple)"""
        # Conversion basique pour l'instant
        html = markdown_content
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n')
        return f"<article>{html}</article>"
    
    def generate_article_schema(self, title: str, content: str, site_context: Dict[str, Any]) -> Dict[str, Any]:
        """Génère le schema.org Article pour l'article"""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "author": {
                "@type": "Person",
                "name": "Expert SEKOIA",
                "jobTitle": "Analyste GEO"
            },
            "publisher": {
                "@type": "Organization",
                "name": site_context.get('site_name', 'SEKOIA'),
                "url": site_context.get('url', '')
            },
            "datePublished": "2025-01-15",
            "dateModified": "2025-01-15"
        }
    
    def estimate_geo_score(self, content: str) -> float:
        """Estime le score GEO de l'article"""
        score = 5.0
        
        # +1 si TL;DR présent
        if 'TL;DR' in content or 'À retenir' in content:
            score += 1.0
        
        # +1 si beaucoup de stats
        stats_count = content.count('%') + content.count('$')
        if stats_count > 10:
            score += 1.0
        
        # +1 si FAQ présente
        if '##  FAQ' in content or 'FAQ' in content:
            score += 1.0
        
        # +0.5 si tableaux
        if '|' in content:  # Markdown table
            score += 0.5
        
        # +0.5 si citation boxes
        if '>' in content:
            score += 0.5
        
        return min(score, 10.0)
