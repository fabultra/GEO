"""
Routes rapports
Export, récupération
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import Analysis, Report
from schemas import ReportExport, ReportResponse
from dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{analysis_id}", response_model=ReportResponse)
async def get_report(
    analysis_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer le rapport d'une analyse

    Si le rapport n'existe pas encore, retourne 404
    """
    user_id = current_user["id"]

    # Vérifier que l'analyse appartient à l'utilisateur
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Récupérer le rapport (par défaut JSON)
    report = db.query(Report).filter(
        Report.analysis_id == analysis_id,
        Report.report_type == 'json'
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not yet generated"
        )

    return report


@router.post("/{analysis_id}/export")
async def export_report(
    analysis_id: str,
    export_data: ReportExport,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Exporter un rapport dans un format spécifique

    Formats supportés: pdf, json, csv, html

    Retourne le fichier directement
    """
    user_id = current_user["id"]

    # Vérifier que l'analyse appartient à l'utilisateur
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == user_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    if not analysis.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis not completed yet"
        )

    # TODO: Générer le rapport dans le format demandé
    # Pour l'instant, retourner 501 Not Implemented

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"Export to {export_data.format} not yet implemented"
    )
