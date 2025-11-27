from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import json
from anthropic import AsyncAnthropic
from visibility_tester import VisibilityTester
from competitive_intelligence import CompetitiveIntelligence
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from scoring_grids import SCORING_GRIDS, get_scoring_prompt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class Lead(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firstName: str
    lastName: str
    email: EmailStr
    company: Optional[str] = None
    url: str
    consent: bool = True
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LeadCreate(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    company: Optional[str] = None
    url: str
    consent: bool = True

class AnalysisJob(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    leadId: str
    url: str
    status: str = "pending"  # pending, processing, completed, failed
    progress: int = 0
    error: Optional[str] = None
    reportId: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Score(BaseModel):
    """
    Modèle de scoring GEO (Generative Engine Optimization).
    Focus sur performance dans les moteurs génératifs (ChatGPT, Claude, Perplexity, etc.)
    """
    structure: float = 0.0          # Structure sémantique optimisée IA
    answerability: float = 0.0      # Capacité à répondre clairement aux questions (NOUVEAU - priorité GEO)
    readability: float = 0.0        # Lisibilité machine/IA avec schémas structurés
    eeat: float = 0.0              # Expertise, Expérience, Autorité, Fiabilité
    educational: float = 0.0        # Valeur éducative et profondeur du contenu
    thematic: float = 0.0          # Cohérence thématique pour compréhension IA
    aiOptimization: float = 0.0    # Optimisation spécifique pour extraction IA
    visibility: float = 0.0         # Visibilité réelle mesurée dans les LLMs
    infoDensity: float = 0.0       # Métrique technique (N'INFLUENCE PLUS le score global GEO)
    global_score: float = 0.0      # Score GEO global pondéré
    
    @staticmethod
    def calculate_weighted_score(scores: dict) -> float:
        """
        Calcule le score GEO global pondéré - 100% Generative Engine Optimization.
        
        Pondération GEO pure (infoDensity exclus volontairement):
        - answerability: 20% (capacité à répondre = priorité #1 pour IA)
        - structure: 15% (formatage extractible par LLM)
        - eeat: 15% (crédibilité pour citation par IA)
        - educational: 15% (profondeur = meilleure compréhension IA)
        - readability: 10% (schémas structurés FAQPage, Article, HowTo)
        - aiOptimization: 10% (TL;DR, réponses directes, listes)
        - thematic: 10% (cohérence thématique)
        - visibility: 5% (performance réelle mesurée)
        """
        weights = {
            'structure': 0.15,
            'answerability': 0.20,     # Nouvelle dimension prioritaire
            'readability': 0.10,
            'eeat': 0.15,
            'educational': 0.15,
            'thematic': 0.10,
            'aiOptimization': 0.10,
            'visibility': 0.05
            # infoDensity: EXCLUS du score global GEO
        }
        
        weighted_sum = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        return round(weighted_sum, 2)

class Recommendation(BaseModel):
    title: str
    criterion: str
    impact: str  # high, medium, low
    effort: str  # high, medium, low
    priority: int
    description: str
    example: Optional[str] = None

class DetailedObservation(BaseModel):
    score_justification: str
    specific_problems: List[str] = []
    positive_points: List[str] = []
    missing_elements: List[str] = []

class QuickWin(BaseModel):
    title: str
    impact: str
    time_required: str
    description: str

class ExecutiveSummary(BaseModel):
    global_assessment: str
    critical_issues: List[str] = []
    key_opportunities: List[str] = []
    estimated_visibility_loss: Optional[str] = None
    recommended_investment: Optional[str] = None

class ROIEstimation(BaseModel):
    current_situation: str
    potential_improvement: str
    timeline: str

class VisibilityResults(BaseModel):
    overall_visibility: float
    platform_scores: Dict[str, float]
    queries_tested: int
    total_tests: int
    details: List[Dict[str, Any]] = []

class Report(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    leadId: str
    url: str
    type: str = "executive"  # executive or complete
    scores: Score
    recommendations: List[Recommendation] = []
    quick_wins: List[QuickWin] = []
    analysis: Optional[Dict[str, Any]] = None
    detailed_observations: Optional[Dict[str, Any]] = None
    executive_summary: Optional[Dict[str, Any]] = None
    roi_estimation: Optional[Dict[str, Any]] = None
    visibility_results: Optional[Dict[str, Any]] = None
    test_queries: Optional[List[str]] = None
    pdfUrl: Optional[str] = None
    docxUrl: Optional[str] = None
    dashboardUrl: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReportCreate(BaseModel):
    leadId: str
    url: str
    type: str = "executive"

# Crawling & Analysis Functions
async def crawl_website(url: str, max_pages: int = 10) -> Dict[str, Any]:
    """Crawl website and extract content"""
    try:
        logger.info(f"Starting crawl for {url}")
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed_url = urlparse(url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        visited = set()
        to_visit = [url]
        pages_data = []
        
        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)
            
            if current_url in visited:
                continue
                
            visited.add(current_url)
            
            try:
                response = requests.get(current_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; GEOBot/1.0)'
                })
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Extract content
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""
                
                meta_desc = soup.find('meta', {'name': 'description'})
                meta_description = meta_desc.get('content', '') if meta_desc else ""
                
                # Extract headings
                h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
                h2_tags = [h.get_text().strip() for h in soup.find_all('h2')]
                h3_tags = [h.get_text().strip() for h in soup.find_all('h3')]
                
                # Extract paragraphs
                paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 50]
                
                # Extract JSON-LD
                json_ld = []
                for script in soup.find_all('script', {'type': 'application/ld+json'}):
                    try:
                        json_ld.append(json.loads(script.string))
                    except:
                        pass
                
                # Extract internal links
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    absolute_url = urljoin(current_url, href)
                    
                    if absolute_url.startswith(base_domain) and absolute_url not in visited and len(to_visit) < 20:
                        # Avoid common non-content pages
                        if not any(x in absolute_url.lower() for x in ['#', 'javascript:', 'mailto:', '.pdf', '.jpg', '.png']):
                            to_visit.append(absolute_url)
                
                page_data = {
                    'url': current_url,
                    'title': title_text,
                    'meta_description': meta_description,
                    'h1': h1_tags,
                    'h2': h2_tags,
                    'h3': h3_tags,
                    'paragraphs': paragraphs[:10],  # First 10 paragraphs
                    'json_ld': json_ld,
                    'word_count': sum(len(p.split()) for p in paragraphs)
                }
                
                pages_data.append(page_data)
                logger.info(f"Crawled: {current_url}")
                
                await asyncio.sleep(0.5)  # Be polite
                
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

async def analyze_with_claude(crawl_data: Dict[str, Any], visibility_data: Dict[str, Any] = None, retry_count: int = 3) -> Dict[str, Any]:
    """Use Claude to analyze crawled content based on 8 GEO criteria - WITH CACHE"""
    
    # ============ CACHE CHECK (économie -30-40% API) ============
    try:
        from services.cache_service import cache_service
        import hashlib
        import json
        
        cache_key_data = {
            'base_url': crawl_data.get('base_url', ''),
            'pages_count': len(crawl_data.get('pages', [])),
            'vis_score': visibility_data.get('overall_visibility', 0) if visibility_data else 0,
            'v': '3'
        }
        cache_key = f"claude_v3_{hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()}"
        
        cached = cache_service.get(cache_key, max_age_hours=168)
        if cached:
            logger.info(f"✅ CACHE HIT - saved ~$0.50 API cost")
            return cached
        logger.info("💰 CACHE MISS - calling Claude...")
    except Exception as e:
        logger.debug(f"Cache check failed: {e}")
    # ===========================================================
    
    try:
        # Utiliser la clé Anthropic directe en priorité, fallback sur Emergent
        api_key = os.environ.get('ANTHROPIC_API_KEY', os.environ.get('EMERGENT_LLM_KEY'))
        
        # Limiter la taille du contenu envoyé à Claude pour éviter les timeouts
        max_pages_to_analyze = 8  # Augmenté à 8 pages pour meilleure analyse
        
        # Prepare content summary for Claude (limité pour éviter timeouts)
        pages_summary = []
        for page in crawl_data['pages'][:max_pages_to_analyze]:
            pages_summary.append({
                'url': page['url'],
                'title': page['title'],
                'h1': page['h1'][:3],  # Limiter à 3 H1
                'h2': page['h2'][:5],
                'content_preview': ' '.join(page['paragraphs'][:2])[:400],  # Réduire preview
                'has_json_ld': len(page['json_ld']) > 0,
                'word_count': page['word_count']
            })
        
        # Construire un prompt optimisé (plus court pour éviter timeouts)
        # Résumé des grilles au lieu du texte complet
        analysis_prompt = f"""
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
- Observations detaillees pour LES 8 criteres (pas seulement structure!)
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
        
        # Retry logic avec backoff exponentiel
        last_error = None
        response_text = None
        
        for attempt in range(retry_count):
            try:
                # Utiliser l'API Anthropic directe
                client = AsyncAnthropic(api_key=api_key)
                
                response = await client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=8192,
                    temperature=0,  # ✅ DÉTERMINISTE
                    system="Vous êtes un expert en GEO. Répondez uniquement en JSON valide.",
                    messages=[
                        {
                            "role": "user",
                            "content": analysis_prompt
                        }
                    ]
                )
                
                # Extraire le texte de la réponse
                response_text = response.content[0].text
                logger.info("Réponse reçue de Claude")
                break  # Succès, sortir de la boucle
                
            except Exception as e:
                last_error = e
                logger.warning(f"Tentative {attempt + 1}/{retry_count} échouée: {str(e)}")
                
                if attempt < retry_count - 1:
                    # Attendre avant de retry (backoff exponentiel)
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.info(f"Attente de {wait_time}s avant retry...")
                    await asyncio.sleep(wait_time)
                else:
                    # Dernière tentative échouée, lever l'erreur
                    logger.error(f"Toutes les tentatives ont échoué: {str(last_error)}")
                    raise last_error
        
        if not response_text:
            raise ValueError("Aucune réponse reçue de Claude")
        
        # Parse JSON response avec nettoyage robuste
        try:
            # Clean response text
            response_text = response_text.strip()
            
            # Enlever les markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            response_text = response_text.strip()
            
            # Tentative de parsing direct
            try:
                analysis_result = json.loads(response_text)
                
                # Valider que les champs essentiels sont présents
                if 'scores' not in analysis_result or 'recommendations' not in analysis_result:
                    raise ValueError("Champs essentiels manquants")
                    
                return analysis_result
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Première tentative de parsing échouée: {str(e)}")
                
                # Tentative 2: Nettoyer les guillemets problématiques
                import re
                # Remplacer les sauts de ligne dans les strings par des espaces
                response_text = re.sub(r'(?<=: ")(.*?)(?="[,\}])', lambda m: m.group(0).replace('\n', ' '), response_text, flags=re.DOTALL)
                
                try:
                    analysis_result = json.loads(response_text)
                    if 'scores' in analysis_result and 'recommendations' in analysis_result:
                        return analysis_result
                except:
                    pass
                
                # Tentative 3: Parser manuellement les scores + générer recommendations séparément
                logger.error(f"Impossible de parser le JSON complet. Extraction des scores + génération recommendations séparée.")
                scores_match = re.search(r'"scores":\s*\{([^}]+)\}', response_text)
                
                if scores_match:
                    scores_text = '{' + scores_match.group(1) + '}'
                    try:
                        scores = json.loads(scores_text)
                        logger.info("Scores extraits avec succès")
                        
                        # NOUVEAU : Générer recommendations et quick_wins avec un appel séparé
                        try:
                            logger.info("Génération séparée des recommendations...")
                            recs_prompt = f"""Genere 15 recommendations et 6 quick wins pour ce site GEO.

SCORES: {json.dumps(scores, indent=2)}

Reponds en JSON valide (pas de markdown, pas de texte):
{{
  "recommendations": [
    {{"title": "Ajouter FAQ", "criterion": "structure", "impact": "high", "effort": "low", "priority": 1, "description": "Creer FAQ avec 20 questions", "example": "Schema FAQPage"}},
    {{"title": "Optimiser meta", "criterion": "readability", "impact": "high", "effort": "low", "priority": 2, "description": "Recrire meta descriptions", "example": "Meta factuelle 120 char"}}
  ],
  "quick_wins": [
    {{"title": "Schema Organization", "impact": "Visibilite IA immediate", "time_required": "1h", "description": "Ajouter JSON-LD Organization"}},
    {{"title": "Section TLDR", "impact": "Meilleur taux extraction", "time_required": "2h", "description": "Resume 40-60 mots debut pages"}}
  ],
  "analysis": {{
    "strengths": ["Bon contenu technique", "Structure claire"],
    "weaknesses": ["Manque FAQ", "Pas de schema"],
    "opportunities": ["Ajouter FAQ", "Optimiser IA"]
  }}
}}

IMPORTANT: Genere 15 recommendations et 6 quick wins minimum."""

                            rec_response = await client.messages.create(
                                model="claude-sonnet-4-5-20250929",
                                max_tokens=3000,
                                temperature=0,  # ✅ DÉTERMINISTE
                                messages=[{"role": "user", "content": recs_prompt}]
                            )
                            
                            rec_text = rec_response.content[0].text.strip()
                            
                            # Nettoyer markdown
                            if '```json' in rec_text:
                                rec_text = rec_text.split('```json')[1].split('```')[0]
                            elif '```' in rec_text:
                                rec_text = rec_text.split('```')[1].split('```')[0]
                            
                            rec_data = json.loads(rec_text.strip())
                            
                            logger.info(f"✅ Recommendations générées: {len(rec_data.get('recommendations', []))} recs, {len(rec_data.get('quick_wins', []))} quick wins")
                            
                            # TOUJOURS générer detailed_observations (car le prompt ne les demande pas)
                            logger.info("Génération des detailed_observations basés sur les scores...")
                            
                            # Générer l'executive summary basé sur les scores et analysis
                            analysis = rec_data.get('analysis', {})
                            weaknesses = analysis.get('weaknesses', [])
                            opportunities = analysis.get('opportunities', [])
                            
                            # Calculer score global
                            global_score = scores.get('global_score', sum(scores.values()) / len(scores))
                            
                            # Assessment basé sur le score
                            if global_score < 4:
                                assessment = f"Le site présente des lacunes critiques en GEO (score {global_score:.1f}/10). Optimisation urgente nécessaire."
                            elif global_score < 6:
                                assessment = f"Le site a des bases correctes (score {global_score:.1f}/10) mais nécessite des améliorations significatives."
                            else:
                                assessment = f"Le site est bien optimisé pour le GEO (score {global_score:.1f}/10) avec des opportunités d'amélioration."
                            
                            # Estimer perte de visibilité
                            visibility_score = scores.get('visibility', 0)
                            if visibility_score < 3:
                                visibility_loss = "80-90%"
                            elif visibility_score < 5:
                                visibility_loss = "60-70%"
                            elif visibility_score < 7:
                                visibility_loss = "40-50%"
                            else:
                                visibility_loss = "20-30%"
                            
                            # Générer detailed_observations basés sur les scores
                            detailed_obs = {}
                            criteria_names = {
                                'structure': 'Structure & Formatage',
                                'infoDensity': 'Densité d\'Information',
                                'readability': 'Lisibilité Machine/SEO',
                                'eeat': 'E-E-A-T',
                                'educational': 'Contenu Éducatif',
                                'thematic': 'Organisation Thématique',
                                'aiOptimization': 'Optimisation IA',
                                'visibility': 'Visibilité Actuelle'
                            }
                            
                            for criterion, score in scores.items():
                                if criterion == 'global_score':
                                    continue
                                    
                                score_val = score if isinstance(score, (int, float)) else 5.0
                                
                                if score_val >= 7:
                                    just = f"{criteria_names.get(criterion, criterion)} bien optimisé avec un score de {score_val:.1f}/10"
                                    positives = ["Score satisfaisant", "Bonnes pratiques en place"]
                                    problems = ["Quelques améliorations mineures possibles"]
                                    missing = ["Optimisations avancées à considérer"]
                                elif score_val >= 5:
                                    just = f"{criteria_names.get(criterion, criterion)} correct mais perfectible (score {score_val:.1f}/10)"
                                    positives = ["Bases correctes"]
                                    problems = ["Manque d'optimisations avancées", "Potentiel d'amélioration significatif"]
                                    missing = ["Optimisations GEO recommandées", "Meilleures pratiques à implémenter"]
                                else:
                                    just = f"{criteria_names.get(criterion, criterion)} nécessite amélioration urgente (score {score_val:.1f}/10)"
                                    positives = ["Potentiel d'amélioration élevé"]
                                    problems = ["Lacunes importantes identifiées", "Non-conformité aux standards GEO", "Impact négatif sur visibilité IA"]
                                    missing = ["Optimisations critiques requises", "Restructuration nécessaire", "Conformité GEO à établir"]
                                
                                detailed_obs[criterion] = {
                                    "score_justification": just,
                                    "positive_points": positives,
                                    "specific_problems": problems,
                                    "missing_elements": missing
                                }
                            
                            # Construire réponse complète
                            return {
                                "scores": scores,
                                "recommendations": rec_data.get('recommendations', [])[:20],
                                "quick_wins": rec_data.get('quick_wins', [])[:8],
                                "analysis": analysis,
                                "detailed_observations": detailed_obs,  # ✅ TOUJOURS GÉNÉRÉ
                                "executive_summary": {
                                    "global_assessment": assessment,
                                    "critical_issues": weaknesses[:3],
                                    "key_opportunities": opportunities[:3],
                                    "estimated_visibility_loss": visibility_loss,
                                    "recommended_investment": f"Phase 1: {15000 + int(global_score * 1000)}€ sur 3-6 mois pour corriger les lacunes critiques"
                                },
                                "roi_estimation": {
                                    "current_situation": f"Score GEO actuel: {global_score:.1f}/10 avec visibilité IA limitée",
                                    "potential_improvement": f"Potentiel d'atteindre {min(global_score + 3, 10):.1f}/10 avec les optimisations recommandées",
                                    "timeline": "6-12 mois pour résultats mesurables"
                                }
                            }
                            
                        except Exception as rec_error:
                            logger.error(f"Génération recommendations séparée échouée: {str(rec_error)}")
                            # Fallback ROBUSTE basé sur les scores
                            recs = []
                            qw = []
                            
                            # Générer recommendations basiques selon les scores faibles
                            if scores.get('structure', 0) < 7:
                                recs.append({"title": "Ajouter sections TL;DR", "criterion": "structure", "impact": "high", "effort": "medium", "priority": 1, "description": "Ajouter un résumé de 40-60 mots en début de chaque page importante", "example": "Résumé factuel avant le contenu principal"})
                            if scores.get('infoDensity', 0) < 7:
                                recs.append({"title": "Enrichir avec statistiques", "criterion": "infoDensity", "impact": "high", "effort": "medium", "priority": 2, "description": "Ajouter des données chiffrées et statistiques factuelles", "example": "Stats secteur, chiffres clés, données marché"})
                            if scores.get('readability', 0) < 7:
                                recs.append({"title": "Implémenter Schema.org", "criterion": "readability", "impact": "high", "effort": "medium", "priority": 3, "description": "Ajouter JSON-LD schemas (Organization, FAQPage, Article)", "example": "Schema Organization pour page accueil"})
                            if scores.get('eeat', 0) < 7:
                                recs.append({"title": "Afficher expertise auteurs", "criterion": "eeat", "impact": "high", "effort": "low", "priority": 4, "description": "Ajouter bio auteurs avec credentials sur chaque article", "example": "Profil auteur avec expertise et certifications"})
                            if scores.get('educational', 0) < 7:
                                recs.append({"title": "Créer contenu éducatif", "criterion": "educational", "impact": "high", "effort": "high", "priority": 5, "description": "Développer 20+ guides pratiques et articles how-to", "example": "Guides détaillés étape par étape"})
                            if scores.get('thematic', 0) < 7:
                                recs.append({"title": "Organiser en silos thématiques", "criterion": "thematic", "impact": "medium", "effort": "high", "priority": 6, "description": "Restructurer contenu en hubs thématiques avec pages satellites", "example": "Hub principal + 10-15 pages satellites"})
                            if scores.get('aiOptimization', 0) < 7:
                                recs.append({"title": "Optimiser format pour IA", "criterion": "aiOptimization", "impact": "high", "effort": "medium", "priority": 7, "description": "Adapter format: listes, tableaux, réponses directes", "example": "Tableaux comparatifs, listes à puces"})
                            if scores.get('visibility', 0) < 7:
                                recs.append({"title": "Améliorer visibilité IA", "criterion": "visibility", "impact": "high", "effort": "high", "priority": 8, "description": "Combiner toutes optimisations GEO pour visibilité", "example": "Plan d'action complet GEO"})
                            
                            # Quick wins basiques
                            qw = [
                                {"title": "Ajouter Schema Organization", "impact": "Visibilité immédiate +30%", "time_required": "1 heure", "description": "Implémenter JSON-LD Organization sur page accueil"},
                                {"title": "Créer page FAQ", "impact": "Citations IA +60%", "time_required": "3 heures", "description": "Page FAQ avec 20 questions + Schema FAQPage"},
                                {"title": "Optimiser 5 meta descriptions", "impact": "Extraction +25%", "time_required": "1 heure", "description": "Réécrire en mode factuel, 120 caractères max"},
                                {"title": "Ajouter TL;DR page accueil", "impact": "Compréhension IA +40%", "time_required": "30 minutes", "description": "Résumé 50 mots en début de page"},
                                {"title": "Structurer en listes", "impact": "Lisibilité IA +35%", "time_required": "2 heures", "description": "Convertir paragraphes en listes à puces"},
                                {"title": "Ajouter statistiques clés", "impact": "Crédibilité +50%", "time_required": "2 heures", "description": "5-10 stats factuelles sur pages piliers"}
                            ]
                            
                            # Analysis basique
                            strengths = []
                            weaknesses = []
                            opportunities = []
                            
                            for key, score in scores.items():
                                if key != 'global_score':
                                    if score >= 7:
                                        strengths.append(f"{key.title()}: score correct ({score:.1f}/10)")
                                    else:
                                        weaknesses.append(f"{key.title()}: nécessite amélioration ({score:.1f}/10)")
                                        opportunities.append(f"Optimiser {key}")
                            
                            # Générer detailed_observations basés sur les scores
                            detailed_obs = {}
                            criteria_names = {
                                'structure': 'Structure & Formatage',
                                'infoDensity': 'Densité d\'Information',
                                'readability': 'Lisibilité Machine/SEO',
                                'eeat': 'E-E-A-T',
                                'educational': 'Contenu Éducatif',
                                'thematic': 'Organisation Thématique',
                                'aiOptimization': 'Optimisation IA',
                                'visibility': 'Visibilité Actuelle'
                            }
                            
                            for criterion, score in scores.items():
                                if criterion == 'global_score':
                                    continue
                                    
                                score_val = score if isinstance(score, (int, float)) else 5.0
                                
                                if score_val >= 7:
                                    just = f"{criteria_names.get(criterion, criterion)} bien optimisé avec un score de {score_val:.1f}/10"
                                    positives = ["Score satisfaisant", "Bonnes pratiques en place"]
                                    problems = ["Quelques améliorations mineures possibles"]
                                    missing = ["Optimisations avancées à considérer"]
                                elif score_val >= 5:
                                    just = f"{criteria_names.get(criterion, criterion)} correct mais perfectible (score {score_val:.1f}/10)"
                                    positives = ["Bases correctes"]
                                    problems = ["Manque d'optimisations avancées", "Potentiel d'amélioration significatif"]
                                    missing = ["Optimisations GEO recommandées", "Meilleures pratiques à implémenter"]
                                else:
                                    just = f"{criteria_names.get(criterion, criterion)} nécessite amélioration urgente (score {score_val:.1f}/10)"
                                    positives = ["Potentiel d'amélioration élevé"]
                                    problems = ["Lacunes importantes identifiées", "Non-conformité aux standards GEO", "Impact négatif sur visibilité IA"]
                                    missing = ["Optimisations critiques requises", "Restructuration nécessaire", "Conformité GEO à établir"]
                                
                                detailed_obs[criterion] = {
                                    "score_justification": just,
                                    "positive_points": positives,
                                    "specific_problems": problems,
                                    "missing_elements": missing
                                }
                            
                            return {
                                "scores": scores,
                                "recommendations": recs[:15],
                                "quick_wins": qw[:8],
                                "analysis": {
                                    "strengths": strengths[:5] if strengths else ["Analyse des scores effectuée"],
                                    "weaknesses": weaknesses[:5] if weaknesses else ["À améliorer"],
                                    "opportunities": opportunities[:5] if opportunities else ["Potentiel d'optimisation"]
                                },
                                "detailed_observations": detailed_obs
                            }
                    except Exception as score_error:
                        logger.error(f"Extraction scores échouée: {str(score_error)}")
                        pass
                
                # Dernier fallback
                raise ValueError("Impossible d'extraire les données")
                
        except Exception as e:
            logger.error(f"Erreur complète de parsing: {str(e)}")
            logger.error(f"Réponse brute (premiers 500 chars): {response_text[:500] if response_text else 'None'}")
            
            # Fallback with default scores
            return {
                "scores": {
                    "structure": 5.0,
                    "infoDensity": 5.0,
                    "readability": 5.0,
                    "eeat": 5.0,
                    "educational": 5.0,
                    "thematic": 5.0,
                    "aiOptimization": 5.0,
                    "visibility": 5.0,
                    "global_score": 5.0
                },
                "recommendations": [{
                    "title": "Erreur d'analyse",
                    "criterion": "general",
                    "impact": "high",
                    "effort": "low",
                    "priority": 1,
                    "description": "L'analyse n'a pas pu être complétée. Veuillez réessayer.",
                    "example": str(e)
                }],
                "analysis": {
                    "strengths": ["À déterminer"],
                    "weaknesses": ["Erreur d'analyse"],
                    "opportunities": ["Réessayer l'analyse"]
                }
            }
            
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise

async def generate_pdf_report(report: Report) -> bytes:
    """Generate PDF report"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title style
        brand_color = os.environ.get('PDF_BRAND_COLOR', '#1a1a1a')
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor(brand_color),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Add title with SEKOIA branding
        org_name = os.environ.get('ORG_NAME', 'SEKOIA')
        story.append(Paragraph(f"Rapport GEO - {org_name}", title_style))
        story.append(Paragraph(f"<b>Type:</b> {report.type.upper()}", styles['Normal']))
        story.append(Paragraph(f"<b>Site:</b> {report.url}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {report.createdAt.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Scores section
        story.append(Paragraph("<b>SCORES GEO</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        # Create scores table
        scores_data = [
            ['Critère', 'Score'],
            ['Structure & Formatage', f"{report.scores.structure:.1f}/10"],
            ['Densité d\'Information', f"{report.scores.infoDensity:.1f}/10"],
            ['Lisibilité Machine/SEO', f"{report.scores.readability:.1f}/10"],
            ['E-E-A-T', f"{report.scores.eeat:.1f}/10"],
            ['Contenu Éducatif', f"{report.scores.educational:.1f}/10"],
            ['Organisation Thématique', f"{report.scores.thematic:.1f}/10"],
            ['Optimisation IA', f"{report.scores.aiOptimization:.1f}/10"],
            ['Visibilité Actuelle', f"{report.scores.visibility:.1f}/10"],
            ['', ''],
            ['SCORE GLOBAL', f"{report.scores.global_score:.1f}/10"],
        ]
        
        scores_table = Table(scores_data, colWidths=[4*inch, 1.5*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(brand_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e5e7eb')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(scores_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations section
        if report.recommendations:
            story.append(Paragraph("<b>RECOMMANDATIONS PRIORITAIRES</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for i, rec in enumerate(report.recommendations[:10], 1):
                story.append(Paragraph(f"<b>{i}. {rec.title}</b>", styles['Heading3']))
                story.append(Paragraph(f"<i>Impact: {rec.impact} | Effort: {rec.effort} | Priorité: {rec.priority}</i>", styles['Normal']))
                story.append(Paragraph(rec.description, styles['Normal']))
                if rec.example:
                    story.append(Paragraph(f"<i>Exemple: {rec.example}</i>", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise

async def process_analysis_job(job_id: str):
    """Background task to process analysis"""
    try:
        # Get job
        job_doc = await db.analysis_jobs.find_one({"id": job_id}, {"_id": 0})
        if not job_doc:
            return
        
        # Update status
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "processing", "progress": 10}}
        )
        
        # Step 1: Crawl website
        crawl_data = await crawl_website(job_doc['url'], max_pages=int(os.environ.get('CRAWL_MAX_PAGES', 10)))
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 40}}
        )
        
        # Step 2: Generate test queries (V2 - Semantic Analysis + 100 queries)
        from query_generator_v2 import generate_queries_with_analysis
        query_results = generate_queries_with_analysis(crawl_data, num_queries=100)
        test_queries = query_results.get('queries', [])
        semantic_analysis = query_results.get('semantic_analysis', {})
        query_breakdown = query_results.get('breakdown', {})
        
        logger.info(f"Generated {len(test_queries)} queries (Non-branded: {query_breakdown.get('non_branded', 0)}, Semi-branded: {query_breakdown.get('semi_branded', 0)}, Branded: {query_breakdown.get('branded', 0)})")
        logger.info(f"Industry detected: {semantic_analysis.get('industry_classification', {}).get('primary_industry', 'unknown')}")
        
        # Quick Win 1: Data Gap Detector
        data_gaps = None
        try:
            from data_gap_detector import DataGapDetector
            data_gap_detector = DataGapDetector()
            industry = semantic_analysis.get('industry_classification', {}).get('primary_industry', 'default')
            data_gaps = data_gap_detector.analyze_data_gaps(crawl_data, industry)
            logger.info(f"Data Gaps: {data_gaps['global_stats']['total_stats_found']}/{data_gaps['global_stats']['expected_minimum']} stats - Severity: {data_gaps['global_stats']['gap_severity']}")
        except Exception as e:
            logger.error(f"Data gap analysis failed: {str(e)}")
        
        # Quick Win 2: Token Budget Simulator
        token_analysis = None
        try:
            from token_analyzer import TokenAnalyzer
            token_analyzer = TokenAnalyzer()
            token_analysis = token_analyzer.analyze_token_budget(crawl_data, 8000)
            logger.info(f"Tokens: {token_analysis['global_analysis']['avg_tokens_per_page']:.0f} avg/page, {token_analysis['global_analysis']['pages_will_truncate']} will truncate - Density: {token_analysis['global_analysis']['density_rating']}")
        except Exception as e:
            logger.error(f"Token analysis failed: {str(e)}")
        
        # Sauvegarder queries_config.json pour personnalisation
        queries_config = {
            'site_url': job_doc['url'],
            'auto_generated_queries': test_queries,
            'manual_queries': [],
            'excluded_queries': [],
            'query_metadata': {q: {'generated_at': datetime.now(timezone.utc).isoformat()} for q in test_queries},
            'semantic_analysis': semantic_analysis,
            'query_breakdown': query_breakdown
        }
        queries_config_path = f"/app/backend/queries_config_{job_id}.json"
        with open(queries_config_path, 'w', encoding='utf-8') as f:
            json.dump(queries_config, f, indent=2, ensure_ascii=False)
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 50}}
        )
        
        # Step 3: Test visibility in AI platforms with detailed diagnosis (V2)
        try:
            from visibility_tester_v2 import test_visibility_with_details
            
            # Extraire le nom de l'entreprise
            company_name = ''
            if crawl_data.get('pages'):
                title = crawl_data['pages'][0].get('title', '')
                if '|' in title:
                    company_name = title.split('|')[0].strip()
                elif '-' in title:
                    company_name = title.split('-')[0].strip()
                else:
                    company_name = title.split()[0] if title else ''
            
            # Test avec diagnostic détaillé
            visibility_data = test_visibility_with_details(test_queries, job_doc['url'], company_name)
            logger.info(f"Visibility test completed with diagnosis: {visibility_data.get('summary', {}).get('global_visibility', 0):.1%}")
            
            logger.info("🏆 Running competitive intelligence...")
            try:
                from utils.competitor_extractor import CompetitorExtractor
                from services.competitor_discovery import competitor_discovery
                
                # Étape 1: Extraire depuis les résultats de visibilité
                competitor_urls = CompetitorExtractor.extract_from_visibility_results(
                    visibility_data, 
                    max_competitors=5
                )
                
                # Filtrer notre propre domaine
                competitor_urls = CompetitorExtractor.filter_self_domain(
                    competitor_urls, 
                    job_doc['url']
                )
                
                logger.info(f"📊 Found {len(competitor_urls)} competitor URLs from visibility results")
                
                # Étape 2: Si pas assez de compétiteurs, utiliser la découverte intelligente
                if len(competitor_urls) < 3:
                    logger.info("🔍 Not enough competitors from visibility, using intelligent discovery...")
                    
                    try:
                        discovered_urls = competitor_discovery.discover_real_competitors(
                            semantic_analysis=semantic_analysis,
                            our_url=job_doc['url'],
                            max_competitors=5
                        )
                        
                        # Combiner et dédupliquer
                        all_urls = list(set(competitor_urls + discovered_urls))
                        competitor_urls = all_urls[:5]
                        
                        logger.info(f"✅ Total competitors after discovery: {len(competitor_urls)}")
                    except Exception as e:
                        logger.error(f"Competitor discovery failed: {e}")
                
                logger.info(f"📊 Final competitor count: {len(competitor_urls)}")
                
                if competitor_urls:
                    ci = CompetitiveIntelligence()
                    
                    # Préparer nos données pour comparaison
                    our_data = {
                        'crawl_data': crawl_data,
                        'semantic_analysis': semantic_analysis,
                        'data_gap_analysis': data_gaps,
                        'visibility_data': visibility_data
                    }
                    
                    competitive_analysis = ci.analyze_competitors(
                        competitors_urls=competitor_urls[:5],
                        visibility_data=visibility_data,
                        our_data=our_data
                    )
                    visibility_data['competitive_intelligence'] = competitive_analysis
                    logger.info(f"✅ CI: {competitive_analysis.get('competitors_analyzed', 0)} analyzed, GEO comparatif calculé")
                else:
                    visibility_data['competitive_intelligence'] = {'competitors_analyzed': 0}
            except Exception as e:
                logger.error(f"❌ CI failed: {str(e)}")
                visibility_data['competitive_intelligence'] = {'error': str(e), 'competitors_analyzed': 0}
            
            # Sauvegarder visibility_results.json
            visibility_results_path = f"/app/backend/visibility_results_{job_id}.json"
            with open(visibility_results_path, 'w', encoding='utf-8') as f:
                json.dump(visibility_data, f, indent=2, ensure_ascii=False)
            
            # Convertir au format attendu par le reste du code
            visibility_data_compat = {
                'overall_visibility': visibility_data.get('summary', {}).get('global_visibility', 0.0),
                'platform_scores': visibility_data.get('summary', {}).get('by_platform', {}),
                'queries_tested': len(visibility_data.get('queries', [])),
                'total_tests': len(visibility_data.get('queries', [])) * 5,
                'details': []
            }
            
            # Ajouter les détails au format attendu
            for query_data in visibility_data.get('queries', []):
                for platform, platform_data in query_data.get('platforms', {}).items():
                    visibility_data_compat['details'].append({
                        'query': query_data['query'],
                        'platform': platform.upper(),
                        'mentioned': platform_data.get('mentioned', False),
                        'answer': platform_data.get('full_response', '')[:500]  # Tronquer pour la DB
                    })
            
        except Exception as e:
            logger.error(f"Visibility test failed: {str(e)}")
            visibility_data = {
                'site_url': job_doc['url'],
                'company_name': '',
                'queries': [],
                'summary': {
                    'total_queries': 0,
                    'global_visibility': 0.0,
                    'by_platform': {}
                }
            }
            visibility_data_compat = {
                'overall_visibility': 0.0,
                'platform_scores': {},
                'queries_tested': 0,
                'total_tests': 0,
                'error': str(e)
            }
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 60}}
        )
        
        # Step 4: Analyze with Claude
        analysis_result = await analyze_with_claude(crawl_data, visibility_data_compat)
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 70}}
        )
        
        # Step 4.5: Competitive Intelligence Analysis
        competitive_data = {}
        try:
            from competitive_intelligence import CompetitiveIntelligence
            from utils.competitor_extractor import CompetitorExtractor
            
            # Extraire les compétiteurs des résultats de visibilité
            competitors_urls = CompetitorExtractor.extract_from_visibility_results(
                visibility_data_compat, 
                max_competitors=5
            )
            
            # Filtrer notre propre domaine
            competitors_urls = CompetitorExtractor.filter_self_domain(
                competitors_urls, 
                job_doc['url']
            )
            
            # Si aucun ou peu de compétiteurs trouvés dans visibility, utiliser la découverte intelligente
            if (not competitors_urls or len(competitors_urls) < 3) and semantic_analysis:
                logger.info("🔍 Using intelligent competitor discovery (Google search + semantic analysis)")
                
                try:
                    from services.competitor_discovery import competitor_discovery
                    
                    # Découvrir de VRAIS compétiteurs via recherche Google
                    discovered_urls = competitor_discovery.discover_real_competitors(
                        semantic_analysis=semantic_analysis,
                        our_url=job_doc['url'],
                        max_competitors=5
                    )
                    
                    if discovered_urls:
                        # Combiner avec les URLs déjà trouvées
                        all_urls = list(set(competitors_urls + discovered_urls))
                        competitors_urls = all_urls[:5]  # Garder top 5
                        logger.info(f"✅ Total competitors after discovery: {len(competitors_urls)}")
                    
                except Exception as e:
                    logger.error(f"Competitor discovery failed: {str(e)}")
                    
                    # Fallback sur Claude si la découverte échoue
                    logger.info("Fallback: Using Claude for competitor suggestions")
                    try:
                        from anthropic import Anthropic
                        anthropic_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
                        
                        industry = semantic_analysis.get('industry_classification', {}).get('primary_industry', '')
                        company_type = semantic_analysis.get('industry_classification', {}).get('company_type', '')
                        
                        if industry and company_type:
                            competitors_urls = await CompetitorExtractor.suggest_competitors_with_claude(
                                industry=industry,
                                company_type=company_type,
                                anthropic_client=anthropic_client,
                                max_competitors=5
                            )
                            
                            if competitors_urls:
                                logger.info(f"✅ Found {len(competitors_urls)} competitors from Claude fallback")
                    except Exception as e2:
                        logger.error(f"Claude fallback also failed: {str(e2)}")
            
            if competitors_urls:
                logger.info(f"Analyzing {len(competitors_urls)} competitors")
                comp_intel = CompetitiveIntelligence()
                competitive_data = comp_intel.analyze_competitors(competitors_urls, visibility_data)
                logger.info(f"Competitive analysis completed: {competitive_data.get('competitors_analyzed', 0)} analyzed")
            else:
                logger.info("No competitors found")
                competitive_data = {
                    'competitors_analyzed': 0,
                    'analyses': [],
                    'comparative_metrics': {},
                    'actionable_insights': []
                }
        except Exception as e:
            logger.error(f"Competitive intelligence failed: {str(e)}")
            competitive_data = {'error': str(e)}
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 75}}
        )
        
        # Step 5: Generate Schema Markup
        schemas_data = {}
        try:
            from schema_generator import SchemaGenerator
            
            schema_gen = SchemaGenerator()
            site_data = {
                'url': job_doc['url'],
                'name': crawl_data.get('pages', [{}])[0].get('title', '').split('|')[0].strip() if crawl_data.get('pages') else '',
                'services': [],
                'business_type': 'ProfessionalService'
            }
            
            schemas_data = schema_gen.generate_all_schemas(site_data, crawl_data)
            
            # Générer le guide d'implémentation
            implementation_guide = schema_gen.generate_implementation_guide(schemas_data, job_doc['url'])
            schemas_data['implementation_guide'] = implementation_guide
            
            logger.info(f"Schema generation completed: {len(schemas_data)} schema types")
        except Exception as e:
            logger.error(f"Schema generation failed: {str(e)}")
            schemas_data = {'error': str(e)}
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 80}}
        )
        
        # Step 5.5: Generate GEO-optimized content (Module 2)
        generated_articles = []
        try:
            logger.info("📝 Module 2: Generating GEO-optimized content...")
            from content_generator import ContentGenerator
            
            content_gen = ContentGenerator()
            
            # Extraire les top opportunités (requêtes à faible visibilité)
            opportunities = []
            if analysis_result.get('recommendations'):
                for rec in analysis_result.get('recommendations', [])[:5]:  # Limiter à 5 pour les coûts
                    opportunities.append({
                        'query': rec.get('action', ''),
                        'competitors_content': ''
                    })
            
            # Préparer le contexte du site
            site_context = {
                'industry': semantic_analysis.get('industry_classification', {}).get('primary_industry', 'services'),
                'site_name': job_doc.get('url', '').replace('https://', '').replace('http://', '').split('/')[0],
                'url': job_doc['url'],
                'expertise': semantic_analysis.get('company_description', {}).get('value_proposition', '')
            }
            
            # Générer les articles
            if opportunities:
                generated_articles = await content_gen.generate_articles(
                    opportunities,
                    site_context
                )
                logger.info(f"✅ Generated {len(generated_articles)} GEO-optimized articles")
            else:
                logger.warning("No opportunities found for content generation")
                
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            generated_articles = []
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 82}}
        )
        
        # Step 6: Create report with enriched data and weighted scoring
        scores_dict = analysis_result['scores']
        
        # Appliquer le scoring pondéré
        weighted_global_score = Score.calculate_weighted_score(scores_dict)
        scores_dict['global_score'] = weighted_global_score
        
        report = Report(
            leadId=job_doc['leadId'],
            url=job_doc['url'],
            type="executive",
            scores=Score(**scores_dict),
            recommendations=[Recommendation(**rec) for rec in analysis_result.get('recommendations', [])[:20]],
            quick_wins=[QuickWin(**qw) for qw in analysis_result.get('quick_wins', [])[:10]],
            analysis=analysis_result.get('analysis'),
            detailed_observations=analysis_result.get('detailed_observations'),
            executive_summary=analysis_result.get('executive_summary'),
            roi_estimation=analysis_result.get('roi_estimation'),
            visibility_results=visibility_data,
            test_queries=test_queries
        )
        
        # Save report
        report_dict = report.model_dump()
        report_dict['createdAt'] = report_dict['createdAt'].isoformat()
        report_dict['scores'] = report.scores.model_dump()
        report_dict['recommendations'] = [rec.model_dump() for rec in report.recommendations]
        report_dict['quick_wins'] = [qw.model_dump() for qw in report.quick_wins]
        report_dict['test_queries'] = test_queries
        report_dict['visibility_results'] = visibility_data_compat
        
        # Ajouter les données des modules avancés
        report_dict['competitive_intelligence'] = competitive_data
        report_dict['schemas'] = schemas_data
        report_dict['semantic_analysis'] = semantic_analysis
        report_dict['query_breakdown'] = query_breakdown
        
        # Ajouter Quick Wins (Phase 1)
        if data_gaps:
            report_dict['data_gap_analysis'] = data_gaps
        if token_analysis:
            report_dict['token_analysis'] = token_analysis
        
        # Ajouter Module 2 (Generated Articles)
        if generated_articles:
            report_dict['generated_articles'] = generated_articles
            logger.info(f"Added {len(generated_articles)} generated articles to report")
        
        await db.reports.insert_one(report_dict)
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 85}}
        )
        
        # Step 6: Generate Word Report (50-70 pages)
        try:
            from word_report_generator import WordReportGenerator
            word_generator = WordReportGenerator()
            word_file_path = f"/app/backend/reports/{report.id}_report.docx"
            word_generator.generate_report(report_dict, word_file_path)
            report_dict['docxUrl'] = f"/reports/{report.id}_report.docx"
            logger.info(f"Word report generated: {word_file_path}")
        except Exception as e:
            logger.error(f"Word report generation failed: {str(e)}")
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 90}}
        )
        
        # Step 7: Generate HTML Dashboard
        try:
            from dashboard_generator import generate_dashboard_html
            dashboard_path = f"/app/backend/dashboards/{report.id}_dashboard.html"
            generate_dashboard_html(report_dict, dashboard_path)
            report_dict['dashboardUrl'] = f"/dashboards/{report.id}_dashboard.html"
            logger.info(f"Dashboard generated: {dashboard_path}")
        except Exception as e:
            logger.error(f"Dashboard generation failed: {str(e)}")
        
        # Step 7.5: Generate Interactive Visibility Dashboard (NEW V2)
        try:
            from dashboard_visibility_generator import generate_interactive_dashboard
            visibility_dashboard_path = f"/app/backend/dashboards/{report.id}_visibility_dashboard.html"
            generate_interactive_dashboard(visibility_data, visibility_dashboard_path)
            report_dict['visibilityDashboardUrl'] = f"/dashboards/{report.id}_visibility_dashboard.html"
            logger.info(f"Interactive visibility dashboard generated: {visibility_dashboard_path}")
        except Exception as e:
            logger.error(f"Visibility dashboard generation failed: {str(e)}")
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 95}}
        )
        
        # Step 8: Save to history and generate alerts
        try:
            from database_manager import DatabaseManager
            
            # Nettoyer report_dict pour enlever les ObjectId non-serializable
            def clean_for_json(obj):
                """Nettoie les ObjectId et autres objets non-sérialisables"""
                if isinstance(obj, dict):
                    return {k: clean_for_json(v) for k, v in obj.items() if k != '_id'}
                elif isinstance(obj, list):
                    return [clean_for_json(item) for item in obj]
                elif hasattr(obj, '__dict__'):
                    return str(obj)
                else:
                    return obj
            
            clean_report_dict = clean_for_json(report_dict)
            
            db_manager = DatabaseManager()
            db_manager.save_analysis(clean_report_dict)
            
            # Comparer avec analyse précédente
            previous = db_manager.get_previous_analysis(job_doc['url'])
            if previous:
                alerts = db_manager.generate_alerts(clean_report_dict, previous)
                if alerts:
                    db_manager.save_alerts(job_doc['url'], alerts)
                    report_dict['alerts'] = alerts
                    logger.info(f"Generated {len(alerts)} alerts")
        except Exception as e:
            logger.error(f"History/alerts failed: {str(e)}")
        
        # Update report with all URLs
        await db.reports.update_one(
            {"id": report.id},
            {"$set": {
                "docxUrl": report_dict.get('docxUrl'),
                "dashboardUrl": report_dict.get('dashboardUrl'),
                "alerts": report_dict.get('alerts', [])
            }}
        )
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {
                "status": "completed",
                "progress": 100,
                "reportId": report.id,
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        logger.info(f"Analysis completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Analysis job error: {str(e)}")
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }}
        )

# API Routes
@api_router.post("/leads", response_model=Lead)
async def create_lead(lead_input: LeadCreate, background_tasks: BackgroundTasks):
    """Submit lead form and start analysis"""
    try:
        # Create lead
        lead = Lead(**lead_input.model_dump())
        lead_dict = lead.model_dump()
        lead_dict['createdAt'] = lead_dict['createdAt'].isoformat()
        
        await db.leads.insert_one(lead_dict)
        
        # Create analysis job
        job = AnalysisJob(
            leadId=lead.id,
            url=lead.url
        )
        
        job_dict = job.model_dump()
        job_dict['createdAt'] = job_dict['createdAt'].isoformat()
        job_dict['updatedAt'] = job_dict['updatedAt'].isoformat()
        
        await db.analysis_jobs.insert_one(job_dict)
        
        # Start background analysis
        background_tasks.add_task(process_analysis_job, job.id)
        
        return lead
        
    except Exception as e:
        logger.error(f"Lead creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get analysis job status"""
    try:
        job = await db.analysis_jobs.find_one({"id": job_id}, {"_id": 0})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Get report by ID"""
    try:
        report = await db.reports.find_one({"id": report_id}, {"_id": 0})
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports/{report_id}/pdf")
async def download_report_pdf(report_id: str):
    """Download PDF report"""
    from fastapi.responses import Response
    
    try:
        report_doc = await db.reports.find_one({"id": report_id}, {"_id": 0})
        if not report_doc:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Reconstruct Report object
        report = Report(
            id=report_doc['id'],
            leadId=report_doc['leadId'],
            url=report_doc['url'],
            type=report_doc['type'],
            scores=Score(**report_doc['scores']),
            recommendations=[Recommendation(**rec) for rec in report_doc.get('recommendations', [])],
            analysis=report_doc.get('analysis'),
            createdAt=datetime.fromisoformat(report_doc['createdAt']) if isinstance(report_doc['createdAt'], str) else report_doc['createdAt']
        )
        
        pdf_bytes = await generate_pdf_report(report)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=rapport-geo-{report_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports/{report_id}/docx")
async def download_report_docx(report_id: str):
    """Download Word report"""
    from fastapi.responses import FileResponse
    import os
    
    try:
        file_path = f"/app/backend/reports/{report_id}_report.docx"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Word report not found")
        
        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"rapport-geo-{report_id}.docx"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DOCX download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/reports/{report_id}/dashboard")
async def view_dashboard(report_id: str):
    """View HTML dashboard"""
    from fastapi.responses import FileResponse
    import os
    
    try:
        file_path = f"/app/backend/dashboards/{report_id}_dashboard.html"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return FileResponse(path=file_path, media_type="text/html")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard view error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/leads")
async def get_all_leads():
    """Get all leads with their reports"""
    try:
        leads = await db.leads.find({}, {"_id": 0}).sort("createdAt", -1).to_list(100)
        
        # Get reports for each lead
        for lead in leads:
            reports = await db.reports.find({"leadId": lead['id']}, {"_id": 0}).to_list(10)
            lead['reports'] = reports
            
            # Get job status
            jobs = await db.analysis_jobs.find({"leadId": lead['id']}, {"_id": 0}).sort("createdAt", -1).to_list(1)
            lead['latestJob'] = jobs[0] if jobs else None
        
        return leads
    except Exception as e:
        logger.error(f"Get leads error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/")
async def root():
    return {"message": "GEO SaaS API", "version": "1.0"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
