"""
Service d'Analyse Sémantique avec Claude
Analyse les sites web selon les 8 critères GEO avec cache intégré
"""
import os
import json
import logging
import asyncio
import re
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class AnalyzerService:
    """Service pour l'analyse sémantique avec Claude"""
    
    def __init__(self):
        """Initialise le service avec la clé API"""
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', os.environ.get('EMERGENT_LLM_KEY'))
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY ou EMERGENT_LLM_KEY requis")
        
        self.model = "claude-sonnet-4-5-20250929"
        self.max_tokens = 8192
        self.temperature = 0  # Déterministe
        self.max_pages_to_analyze = 8
    
    async def analyze_with_claude(
        self, 
        crawl_data: Dict[str, Any], 
        visibility_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 3,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analyse un site avec Claude selon les 8 critères GEO
        
        Args:
            crawl_data: Données du crawling (pages, contenu)
            visibility_data: Résultats des tests de visibilité IA (optionnel)
            retry_count: Nombre de tentatives en cas d'échec
            use_cache: Utiliser le cache (défaut: True)
            
        Returns:
            Dict contenant scores, observations, recommendations, quick_wins
        """
        
        # ============ CACHE CHECK ============
        cached_result = None
        cache_key = None
        
        if use_cache:
            try:
                cached_result, cache_key = await self._check_cache(crawl_data, visibility_data)
                if cached_result:
                    logger.info("✅ CACHE HIT - saved ~$0.50 API cost")
                    return cached_result
                logger.info("💰 CACHE MISS - calling Claude...")
            except Exception as e:
                logger.debug(f"Cache check failed: {e}")
        # =====================================
        
        # Préparer les données pour Claude
        pages_summary = self._prepare_pages_summary(crawl_data)
        analysis_prompt = self._build_analysis_prompt(crawl_data, pages_summary, visibility_data)
        
        # Appeler Claude avec retry
        response_text = await self._call_claude_with_retry(analysis_prompt, retry_count)
        
        # Parser la réponse JSON
        analysis_result = await self._parse_claude_response(response_text)
        
        # Sauvegarder en cache si activé
        if use_cache and cache_key:
            try:
                from services.cache_service import cache_service
                cache_service.set(cache_key, analysis_result)
                logger.info("💾 Résultat sauvegardé en cache")
            except Exception as e:
                logger.debug(f"Cache save failed: {e}")
        
        return analysis_result
    
    async def _check_cache(
        self, 
        crawl_data: Dict[str, Any], 
        visibility_data: Optional[Dict[str, Any]]
    ) -> tuple[Optional[Dict], Optional[str]]:
        """Vérifie si le résultat est en cache"""
        try:
            from services.cache_service import cache_service
            import hashlib
            
            cache_key_data = {
                'base_url': crawl_data.get('base_url', ''),
                'pages_count': len(crawl_data.get('pages', [])),
                'vis_score': visibility_data.get('overall_visibility', 0) if visibility_data else 0,
                'v': '3'
            }
            cache_key = f"claude_v3_{hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()}"
            
            cached = cache_service.get(cache_key, max_age_hours=168)  # 7 jours
            return cached, cache_key
        except Exception as e:
            logger.debug(f"Cache check error: {e}")
            return None, None
    
    def _prepare_pages_summary(self, crawl_data: Dict[str, Any]) -> list:
        """Prépare un résumé des pages pour Claude"""
        pages_summary = []
        
        for page in crawl_data['pages'][:self.max_pages_to_analyze]:
            pages_summary.append({
                'url': page['url'],
                'title': page['title'],
                'h1': page['h1'][:3],  # Limiter à 3 H1
                'h2': page['h2'][:5],  # Limiter à 5 H2
                'content_preview': ' '.join(page['paragraphs'][:2])[:400],
                'has_json_ld': len(page['json_ld']) > 0,
                'word_count': page['word_count']
            })
        
        return pages_summary
    
    def _build_analysis_prompt(
        self, 
        crawl_data: Dict[str, Any], 
        pages_summary: list,
        visibility_data: Optional[Dict[str, Any]]
    ) -> str:
        """Construit le prompt d'analyse pour Claude"""
        
        prompt = f"""
VOUS ÊTES UN EXPERT GEO - ANALYSE RIGOUREUSE REQUISE

IMPORTANT: Répondez UNIQUEMENT en JSON valide. N'ajoutez AUCUN texte avant ou après le JSON.
Les descriptions doivent être sur UNE SEULE ligne (pas de sauts de ligne).
Échappez les guillemets dans les textes avec \\"

Analysez ce site web selon 8 critères GEO avec notation 0-10 JUSTIFIÉE.

GRILLES DE SCORING (0-10):
• Structure: 9-10=TL;DR partout + réponses directes | 7-8=Bonne structure | 5-6=Structure basique | 3-4=Faible | 0-2=Aucune structure GEO
• Densité Info: 9-10=Stats abondantes + données originales | 7-8=Bonnes stats | 5-6=Quelques stats | 3-4=Peu de données | 0-2=Aucune stat/donnée factuelle
• Lisibilité Machine: 9-10=Schema complet + JSON-LD | 7-8=Schema principal | 5-6=Schema basique | 3-4=Schema incomplet | 0-2=Aucun schema
• E-E-A-T: 9-10=Auteurs experts identifiés + certifications | 7-8=Bons auteurs | 5-6=Org crédible, auteurs anonymes | 3-4=Faible E-E-A-T | 0-2=Aucun E-E-A-T
• Éducatif: 9-10=50+ guides + FAQ + glossaires | 7-8=20-50 guides | 5-6=10-20 articles | 3-4=<10 articles | 0-2=Aucun contenu éducatif, 100% marketing
• Thématique: 9-10=5+ hubs avec satellites | 7-8=3-5 hubs | 5-6=Début clustering | 3-4=Pas de silos | 0-2=Aucune organisation
• Optimisation IA: 9-10=Format optimal + réponses rapides | 7-8=Bon format | 5-6=Format acceptable | 3-4=Peu adapté IA | 0-2=Format anti-IA (marketing lourd)
• Visibilité: 9-10=Très visible dans IA | 7-8=Visible | 5-6=Occasionnelle | 3-4=Très faible | 0-2=Invisible dans toutes IA

SITE ANALYSÉ: {crawl_data['base_url']} | Pages: {crawl_data['pages_crawled']}

CONTENU:
{json.dumps(pages_summary, ensure_ascii=False, indent=2)}

DONNÉES DE VISIBILITÉ IA:
{json.dumps(visibility_data, ensure_ascii=False, indent=2) if visibility_data else "Aucune donnée de visibilité disponible"}

INSTRUCTIONS:
Pour CHAQUE critère: score 0-10 justifié + problèmes spécifiques + exemples concrets du site

IMPORTANT pour Critères 7 & 8:
- Utilisez les VRAIES données de visibilité ci-dessus
- Critère 7 (aiOptimization): Basez le score sur platform_scores
- Critère 8 (visibility): Basez le score sur overall_visibility
- Convertissez les % en scores 0-10 (ex: 40% = 4.0/10)

JSON REQUIS (RESPECTEZ CE FORMAT EXACTEMENT):
{{
  "scores": {{"structure": 7.5, "infoDensity": 3.0, "readability": 5.0, "eeat": 6.0, "educational": 2.0, "thematic": 4.5, "aiOptimization": 3.5, "visibility": 2.5, "global_score": 4.25}},
  "detailed_observations": {{
    "structure": {{
      "score_justification": "Justification courte et precise du score",
      "positive_points": ["Point fort 1", "Point fort 2"],
      "specific_problems": ["Probleme 1", "Probleme 2", "Probleme 3"],
      "missing_elements": ["Element manquant 1", "Element manquant 2"]
    }},
    "infoDensity": {{
      "score_justification": "Justification courte",
      "positive_points": ["Point fort 1", "Point fort 2"],
      "specific_problems": ["Probleme 1", "Probleme 2"],
      "missing_elements": ["Element manquant 1", "Element manquant 2"]
    }},
    "readability": {{
      "score_justification": "Justification courte",
      "positive_points": ["Point fort 1", "Point fort 2"],
      "specific_problems": ["Probleme 1", "Probleme 2"],
      "missing_elements": ["Element manquant 1", "Element manquant 2"]
    }},
    "eeat": {{
      "score_justification": "Justification courte",
      "positive_points": ["Point fort 1", "Point fort 2"],
      "specific_problems": ["Probleme 1", "Probleme 2"],
      "missing_elements": ["Element manquant 1", "Element manquant 2"]
    }},
    "educational": {{
      "score_justification": "Justification courte",
      "positive_points": ["Point fort 1", "Point fort 2"],
      "specific_problems": ["Probleme 1", "Probleme 2"],
      "missing_elements": ["Element manquant 1", "Element manquant 2"]
    }},
    "thematic": {{
      "score_justification": "Justification courte",
      "positive_points": ["Point fort 1", "Point fort 2"],
      "specific_problems": ["Probleme 1", "Probleme 2"],
      "missing_elements": ["Element manquant 1", "Element manquant 2"]
    }},
    "aiOptimization": {{
      "score_justification": "Justification courte",
      "positive_points": ["Point fort 1", "Point fort 2"],
      "specific_problems": ["Probleme 1", "Probleme 2"],
      "missing_elements": ["Element manquant 1", "Element manquant 2"]
    }},
    "visibility": {{
      "score_justification": "Justification courte",
      "positive_points": ["Point fort 1", "Point fort 2"],
      "specific_problems": ["Probleme 1", "Probleme 2"],
      "missing_elements": ["Element manquant 1", "Element manquant 2"]
    }}
  }},
  "recommendations": [
    {{"title": "Ajouter des FAQ structurees", "criterion": "educational", "impact": "high", "effort": "medium", "priority": 1, "description": "Creer une section FAQ avec 20 questions sur une ligne", "example": "Schema FAQPage JSON-LD"}},
    {{"title": "Optimiser meta descriptions", "criterion": "readability", "impact": "high", "effort": "low", "priority": 2, "description": "Recrire toutes les meta en mode factuel sous 120 caracteres", "example": "Meta actuelle vs meta optimisee"}}
  ],
  "quick_wins": [
    {{"title": "Ajouter Schema Organization", "impact": "Visibilite immediate dans IA", "time_required": "1 heure", "description": "Implementer JSON-LD Organization sur page accueil"}},
    {{"title": "Creer section TL;DR", "impact": "Meilleur taux extraction IA", "time_required": "2 heures", "description": "Ajouter resume 40-60 mots debut de chaque page pilier"}}
  ],
  "analysis": {{"strengths": ["Force 1 detaillee"], "weaknesses": ["Faiblesse 1 detaillee"], "opportunities": ["Opportunite 1 avec potentiel"]}},
  "executive_summary": {{"global_assessment": "Evaluation en 2 phrases sans saut de ligne", "critical_issues": ["Probleme critique 1"], "key_opportunities": ["Opportunite majeure 1"], "estimated_visibility_loss": "60-70%", "recommended_investment": "Phase 1: 15-20k budget sur 3 mois"}},
  "roi_estimation": {{"current_situation": "Situation actuelle en une phrase", "potential_improvement": "Amelioration potentielle en une phrase", "timeline": "6-12 mois pour resultats"}}
}}

RAPPEL CRITIQUE:
- JSON valide UNIQUEMENT (pas de texte avant/apres)
- Descriptions sur UNE seule ligne
- **OBLIGATOIRE: Exactement 20 recommendations** (pas moins!)
- **OBLIGATOIRE: Exactement 8 quick_wins** (pas moins!)
- Observations detaillees pour LES 8 criteres
- Guillemets echappes avec \\"
- Chaque recommendation doit etre CONCRETE et ACTIONNABLE

IMPORTANT: Remplissez detailed_observations pour CHAQUE critere: structure, infoDensity, readability, eeat, educational, thematic, aiOptimization, visibility

VOUS DEVEZ GÉNÉRER 20 RECOMMENDATIONS VARIÉES COUVRANT:
- Structure et format (3-4 recs)
- Contenu et densité info (3-4 recs)
- Schema et données structurées (3-4 recs)
- E-E-A-T et crédibilité (2-3 recs)
- Contenu éducatif (2-3 recs)
- Organisation thématique (2-3 recs)
- Optimisation IA (2-3 recs)
"""
        return prompt
    
    async def _call_claude_with_retry(self, prompt: str, retry_count: int) -> str:
        """Appelle Claude avec retry automatique en cas d'échec"""
        last_error = None
        response_text = None
        
        for attempt in range(retry_count):
            try:
                client = AsyncAnthropic(api_key=self.api_key)
                
                response = await client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system="Vous êtes un expert en GEO. Répondez uniquement en JSON valide.",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                response_text = response.content[0].text
                logger.info("Réponse reçue de Claude")
                break  # Succès
                
            except Exception as e:
                last_error = e
                logger.warning(f"Tentative {attempt + 1}/{retry_count} échouée: {str(e)}")
                
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # Backoff exponentiel: 1s, 2s, 4s
                    logger.info(f"Attente de {wait_time}s avant retry...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Toutes les tentatives ont échoué: {str(last_error)}")
                    raise last_error
        
        if not response_text:
            raise ValueError("Aucune réponse reçue de Claude")
        
        return response_text
    
    async def _parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse la réponse JSON de Claude avec nettoyage robuste"""
        
        # Nettoyer la réponse
        response_text = response_text.strip()
        
        # Enlever les markdown code blocks
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        response_text = response_text.strip()
        
        # Tentative 1: Parsing direct
        try:
            analysis_result = json.loads(response_text)
            
            if 'scores' not in analysis_result or 'recommendations' not in analysis_result:
                raise ValueError("Champs essentiels manquants")
            
            return analysis_result
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Première tentative de parsing échouée: {str(e)}")
            
            # Tentative 2: Nettoyer les sauts de ligne dans les strings
            response_text = re.sub(
                r'(?<=: ")(.*?)(?="[,\}])', 
                lambda m: m.group(0).replace('\n', ' '), 
                response_text, 
                flags=re.DOTALL
            )
            
            try:
                analysis_result = json.loads(response_text)
                if 'scores' in analysis_result and 'recommendations' in analysis_result:
                    return analysis_result
            except Exception:
                pass
            
            # Tentative 3: Extraction manuelle des scores + génération recommendations
            logger.error("Impossible de parser le JSON complet. Extraction manuelle...")
            return await self._fallback_parse(response_text)
    
    async def _fallback_parse(self, response_text: str) -> Dict[str, Any]:
        """Parsing de secours quand le JSON est invalide"""
        
        # Extraire les scores
        scores_match = re.search(r'"scores":\s*\{([^}]+)\}', response_text)
        
        if scores_match:
            scores_text = '{' + scores_match.group(1) + '}'
            try:
                scores = json.loads(scores_text)
                logger.info("Scores extraits avec succès")
                
                # Générer les recommendations séparément
                logger.info("Génération séparée des recommendations...")
                recommendations = await self._generate_recommendations_fallback(scores)
                
                return {
                    'scores': scores,
                    'recommendations': recommendations,
                    'quick_wins': [],  # Sera rempli par le fallback
                    'analysis': {'strengths': [], 'weaknesses': [], 'opportunities': []},
                    'detailed_observations': {},
                    'executive_summary': {
                        'global_assessment': 'Analyse partielle générée',
                        'critical_issues': [],
                        'key_opportunities': []
                    }
                }
            except Exception as e:
                logger.error(f"Échec extraction scores: {e}")
        
        # Dernier recours: scores par défaut
        logger.error("Utilisation des scores par défaut")
        return {
            'scores': {
                'structure': 5.0,
                'infoDensity': 5.0,
                'readability': 5.0,
                'eeat': 5.0,
                'educational': 5.0,
                'thematic': 5.0,
                'aiOptimization': 5.0,
                'visibility': 5.0,
                'global_score': 5.0
            },
            'recommendations': [],
            'quick_wins': [],
            'analysis': {'strengths': [], 'weaknesses': [], 'opportunities': []},
            'detailed_observations': {},
            'executive_summary': {
                'global_assessment': 'Erreur de parsing - analyse incomplète',
                'critical_issues': ['Erreur lors de l\'analyse'],
                'key_opportunities': []
            }
        }
    
    async def _generate_recommendations_fallback(self, scores: Dict) -> list:
        """Génère des recommendations de base basées sur les scores"""
        recommendations = []
        priority = 1
        
        # Générer recs basées sur les faibles scores
        for criterion, score in scores.items():
            if criterion == 'global_score':
                continue
                
            if score < 6.0:
                recommendations.append({
                    'title': f'Améliorer {criterion}',
                    'criterion': criterion,
                    'impact': 'high' if score < 4.0 else 'medium',
                    'effort': 'medium',
                    'priority': priority,
                    'description': f'Score actuel: {score}/10 - Optimisation requise',
                    'example': 'À définir selon contexte'
                })
                priority += 1
        
        return recommendations


# Instance globale du service
analyzer_service = AnalyzerService()
