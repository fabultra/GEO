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
    structure: float = 0.0
    infoDensity: float = 0.0
    readability: float = 0.0
    eeat: float = 0.0
    educational: float = 0.0
    thematic: float = 0.0
    aiOptimization: float = 0.0
    visibility: float = 0.0
    global_score: float = 0.0
    
    @staticmethod
    def calculate_weighted_score(scores: dict) -> float:
        """Calcule le score global pondéré selon la méthodologie GEO"""
        weights = {
            'structure': 0.15,
            'infoDensity': 0.20,
            'readability': 0.10,
            'eeat': 0.15,
            'educational': 0.20,
            'thematic': 0.05,
            'aiOptimization': 0.10,
            'visibility': 0.05
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
    """Use Claude to analyze crawled content based on 8 GEO criteria"""
    try:
        # Utiliser la clé Anthropic directe en priorité, fallback sur Emergent
        api_key = os.environ.get('ANTHROPIC_API_KEY', os.environ.get('EMERGENT_LLM_KEY'))
        
        # Limiter la taille du contenu envoyé à Claude pour éviter les timeouts
        max_pages_to_analyze = 3  # Réduire de 5 à 3 pages pour éviter les timeouts
        
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
    "structure": {{"score_justification": "Description courte sur UNE ligne", "specific_problems": ["Probleme 1 sans saut de ligne"], "positive_points": ["Point fort 1"], "missing_elements": ["Element manquant 1"]}},
    "infoDensity": {{"score_justification": "...", "specific_problems": ["..."], "positive_points": ["..."], "missing_elements": ["..."]}},
    "readability": {{"score_justification": "...", "specific_problems": ["..."], "positive_points": ["..."], "missing_elements": ["..."]}},
    "eeat": {{"score_justification": "...", "specific_problems": ["..."], "positive_points": ["..."], "missing_elements": ["..."]}},
    "educational": {{"score_justification": "...", "specific_problems": ["..."], "positive_points": ["..."], "missing_elements": ["..."]}},
    "thematic": {{"score_justification": "...", "specific_problems": ["..."], "positive_points": ["..."], "missing_elements": ["..."]}},
    "aiOptimization": {{"score_justification": "...", "specific_problems": ["..."], "positive_points": ["..."], "missing_elements": ["..."]}},
    "visibility": {{"score_justification": "...", "specific_problems": ["..."], "positive_points": ["..."], "missing_elements": ["..."]}}
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
- MINIMUM 15 recommendations (donnez-en 15-20!)
- MINIMUM 5 quick_wins (donnez-en 5-7!)
- Observations detaillees pour LES 8 criteres (pas seulement structure!)
- Guillemets echappes avec \\"

IMPORTANT: Remplissez detailed_observations pour CHAQUE critere: structure, infoDensity, readability, eeat, educational, thematic, aiOptimization, visibility
"""
        
        # Retry logic avec backoff exponentiel
        last_error = None
        response_text = None
        
        for attempt in range(retry_count):
            try:
                # Utiliser l'API Anthropic directe
                client = AsyncAnthropic(api_key=api_key)
                
                response = await client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=8192,
                    temperature=0.3,
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
                
                # Tentative 3: Parser manuellement les scores au minimum
                logger.error(f"Impossible de parser le JSON complet. Extraction des scores uniquement.")
                scores_match = re.search(r'"scores":\s*\{([^}]+)\}', response_text)
                
                if scores_match:
                    scores_text = '{' + scores_match.group(1) + '}'
                    try:
                        scores = json.loads(scores_text)
                        logger.info("Scores extraits avec succès")
                        
                        # Construire une réponse minimale valide
                        return {
                            "scores": scores,
                            "recommendations": [{
                                "title": "Analyse partielle - Rapport incomplet",
                                "criterion": "general",
                                "impact": "high",
                                "effort": "medium",
                                "priority": 1,
                                "description": "L'analyse complète n'a pas pu être générée. Veuillez relancer l'analyse.",
                                "example": "Erreur de parsing JSON"
                            }],
                            "analysis": {
                                "strengths": ["Scores générés"],
                                "weaknesses": ["Rapport incomplet"],
                                "opportunities": ["Relancer l'analyse"]
                            }
                        }
                    except:
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
        
        # Step 2: Generate test queries
        from query_generator import generate_test_queries
        test_queries = generate_test_queries(job_doc['url'], crawl_data)
        logger.info(f"Generated {len(test_queries)} test queries")
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 50}}
        )
        
        # Step 3: Test visibility in AI platforms (critère 7 & 8)
        try:
            tester = VisibilityTester()
            visibility_data = await tester.test_visibility(job_doc['url'], test_queries)
            logger.info(f"Visibility test completed: {visibility_data['overall_visibility']:.1%}")
        except Exception as e:
            logger.error(f"Visibility test failed: {str(e)}")
            visibility_data = {
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
        analysis_result = await analyze_with_claude(crawl_data, visibility_data)
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 75}}
        )
        
        # Step 5: Create report with enriched data and weighted scoring
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
        report_dict['visibility_results'] = visibility_data
        
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
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 95}}
        )
        
        # Step 8: Save to history and generate alerts
        try:
            from database_manager import DatabaseManager
            db_manager = DatabaseManager()
            db_manager.save_analysis(report_dict)
            
            # Comparer avec analyse précédente
            previous = db_manager.get_previous_analysis(job_doc['url'])
            if previous:
                alerts = db_manager.generate_alerts(report_dict, previous)
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
