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
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
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
    pdfUrl: Optional[str] = None
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

async def analyze_with_claude(crawl_data: Dict[str, Any]) -> Dict[str, Any]:
    """Use Claude to analyze crawled content based on 8 GEO criteria"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Prepare content summary for Claude
        pages_summary = []
        for page in crawl_data['pages'][:5]:  # Analyze first 5 pages
            pages_summary.append({
                'url': page['url'],
                'title': page['title'],
                'h1': page['h1'],
                'h2': page['h2'][:5],
                'content_preview': ' '.join(page['paragraphs'][:3])[:500],
                'has_json_ld': len(page['json_ld']) > 0,
                'word_count': page['word_count']
            })
        
        # Construire le prompt amélioré avec grilles d'évaluation
        scoring_grids_text = get_scoring_prompt()
        
        analysis_prompt = f"""
{scoring_grids_text}

========================================
SITE À ANALYSER
========================================

URL: {crawl_data['base_url']}
Pages crawlées: {crawl_data['pages_crawled']}

CONTENU EXTRAIT:
{json.dumps(pages_summary, ensure_ascii=False, indent=2)}

========================================
INSTRUCTIONS D'ANALYSE
========================================

Vous devez produire une analyse GEO DÉTAILLÉE et RIGOUREUSE en suivant EXACTEMENT les grilles d'évaluation fournies.

Pour CHAQUE critère, vous devez:
1. Examiner les éléments spécifiques listés dans la grille
2. Identifier les problèmes concrets avec EXEMPLES du site
3. Comparer avec les best practices GEO
4. Attribuer un score 0-10 JUSTIFIÉ selon la grille
5. Fournir des observations détaillées

FORMAT DE RÉPONSE (JSON valide obligatoire):
{{
  "scores": {{
    "structure": float (0-10),
    "infoDensity": float (0-10),
    "readability": float (0-10),
    "eeat": float (0-10),
    "educational": float (0-10),
    "thematic": float (0-10),
    "aiOptimization": float (0-10),
    "visibility": float (0-10),
    "global_score": float (moyenne pondérée)
  }},
  "detailed_observations": {{
    "structure": {{
      "score_justification": "Pourquoi ce score?",
      "specific_problems": ["Problème 1 avec exemple", "Problème 2 avec exemple"],
      "positive_points": ["Point fort 1", "Point fort 2"],
      "missing_elements": ["Élément manquant 1", "Élément manquant 2"]
    }},
    "infoDensity": {{
      "score_justification": "Pourquoi ce score?",
      "specific_problems": ["Ex: Aucune statistique trouvée sur les pages analysées"],
      "positive_points": ["Points forts s'il y en a"],
      "missing_elements": ["Ex: Pas de données chiffrées, pas de sources citées"]
    }},
    "readability": {{
      "score_justification": "Pourquoi ce score?",
      "specific_problems": ["Ex: Meta descriptions marketing non-factuelles"],
      "positive_points": ["Ex: Structure HTML correcte"],
      "missing_elements": ["Ex: Aucun schema.org détecté dans JSON-LD"]
    }},
    "eeat": {{
      "score_justification": "Pourquoi ce score?",
      "specific_problems": ["Ex: Aucun auteur identifié"],
      "positive_points": ["Ex: Organisation établie depuis X années"],
      "missing_elements": ["Ex: Pas de certifications affichées"]
    }},
    "educational": {{
      "score_justification": "Pourquoi ce score?",
      "specific_problems": ["Ex: Contenu 100% marketing, aucun guide éducatif"],
      "positive_points": ["Points forts s'il y en a"],
      "missing_elements": ["Ex: Pas de FAQ, pas de glossaire, pas de tutoriels"]
    }},
    "thematic": {{
      "score_justification": "Pourquoi ce score?",
      "specific_problems": ["Ex: Pas de maillage interne visible"],
      "positive_points": ["Ex: Structure de navigation claire"],
      "missing_elements": ["Ex: Pas de pages piliers, pas de silos thématiques"]
    }},
    "aiOptimization": {{
      "score_justification": "Pourquoi ce score?",
      "specific_problems": ["Ex: Aucune réponse directe en début de page"],
      "positive_points": ["Points forts s'il y en a"],
      "missing_elements": ["Ex: Pas de TL;DR, pas de format conversationnel"]
    }},
    "visibility": {{
      "score_justification": "Pourquoi ce score?",
      "specific_problems": ["Ex: Contenu probablement invisible dans les IA"],
      "positive_points": ["Ex: Domaine établi"],
      "missing_elements": ["Ex: Pas de contenu citable"]
    }}
  }},
  "recommendations": [
    {{
      "title": "Titre actionnable",
      "criterion": "structure|infoDensity|readability|eeat|educational|thematic|aiOptimization|visibility",
      "impact": "high|medium|low",
      "effort": "high|medium|low",
      "priority": 1-15,
      "description": "Description détaillée (100-200 mots) expliquant le problème, pourquoi c'est important, et comment le résoudre",
      "example": "Exemple CONCRET avec code/texte si applicable"
    }}
  ],
  "quick_wins": [
    {{
      "title": "Action rapide",
      "impact": "Impact attendu",
      "time_required": "Temps estimé",
      "description": "Quoi faire exactement"
    }}
  ],
  "analysis": {{
    "strengths": ["Force 1 avec détail", "Force 2 avec détail", "Force 3"],
    "weaknesses": ["Faiblesse 1 détaillée", "Faiblesse 2 détaillée", "Faiblesse 3"],
    "opportunities": ["Opportunité 1 avec potentiel", "Opportunité 2", "Opportunité 3"]
  }},
  "executive_summary": {{
    "global_assessment": "Évaluation globale en 2-3 phrases",
    "critical_issues": ["Problème critique 1", "Problème critique 2"],
    "key_opportunities": ["Opportunité majeure 1", "Opportunité majeure 2"],
    "estimated_visibility_loss": "Pourcentage de visibilité perdue estimé",
    "recommended_investment": "Phase 1 (3 mois): Budget estimé et actions"
  }},
  "roi_estimation": {{
    "current_situation": "Description de la situation actuelle",
    "potential_improvement": "Amélioration potentielle avec GEO",
    "timeline": "6-12 mois pour résultats significatifs"
  }}
}}

EXIGENCES STRICTES:
- Minimum 15 recommandations détaillées
- 5-7 quick wins actionnables immédiatement
- Observations spécifiques pour CHAQUE critère
- Exemples concrets tirés du contenu analysé
- Justifications rigoureuses des scores
- Comparaisons avec best practices 2025
"""
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"analysis_{uuid.uuid4()}",
            system_message="Vous êtes un expert en GEO. Répondez uniquement en JSON valide."
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        user_message = UserMessage(text=analysis_prompt)
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            response_text = response.strip()
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            analysis_result = json.loads(response_text)
            return analysis_result
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
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
                "recommendations": [],
                "analysis": {
                    "strengths": ["Analyse en cours"],
                    "weaknesses": ["Données insuffisantes"],
                    "opportunities": ["À déterminer"]
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
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Add title
        story.append(Paragraph(f"Rapport GEO - {report.type.upper()}", title_style))
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
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
        
        # Step 2: Analyze with Claude
        analysis_result = await analyze_with_claude(crawl_data)
        
        await db.analysis_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 70}}
        )
        
        # Step 3: Create report
        report = Report(
            leadId=job_doc['leadId'],
            url=job_doc['url'],
            type="executive",
            scores=Score(**analysis_result['scores']),
            recommendations=[Recommendation(**rec) for rec in analysis_result.get('recommendations', [])[:15]],
            analysis=analysis_result.get('analysis')
        )
        
        # Save report
        report_dict = report.model_dump()
        report_dict['createdAt'] = report_dict['createdAt'].isoformat()
        report_dict['scores'] = report.scores.model_dump()
        report_dict['recommendations'] = [rec.model_dump() for rec in report.recommendations]
        
        await db.reports.insert_one(report_dict)
        
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
