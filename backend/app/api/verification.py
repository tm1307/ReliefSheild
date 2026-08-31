from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
import json
import time

from app.core.database import get_db
from app.models.evidence import Appeal, TrustReport, VerificationResult
from app.services.extraction_layer import ExtractionLayer
from app.services.identity_module import IdentityModule
from app.services.payment_module import PaymentModule
from app.services.similarity_module import SimilarityModule
from app.services.claim_module import ClaimModule
from app.services.scoring_engine import ScoringEngine
from app.services.evidence_graph import EvidenceGraphBuilder

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(TrustReport.id)))
    total = result.scalar_one() or 0
    
    if total == 0:
        return {"total_appeals": 0, "avg_score": 0, "flagged_count": 0}
        
    result = await db.execute(select(func.avg(TrustReport.score)))
    avg_score = result.scalar_one() or 0
    
    result = await db.execute(select(func.count(TrustReport.id)).where(TrustReport.score < 50))
    flagged = result.scalar_one() or 0
    
    return {
        "total_appeals": total,
        "avg_score": round(float(avg_score)),
        "flagged_count": flagged
    }

@router.get("/reports/{appeal_id}")
async def get_report(appeal_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TrustReport).where(TrustReport.appeal_id == appeal_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this appeal.")

    graph = json.loads(report.evidence_graph) if report.evidence_graph else {}

    ver_result = await db.execute(
        select(VerificationResult).where(VerificationResult.appeal_id == appeal_id)
    )
    ver_records = ver_result.scalars().all()
    
    # Recalculate breakdown to include points deducted for historical reports
    breakdown = []
    for vr in ver_records:
        pts = 0
        if vr.status == 'Flagged':
            pts = int(ScoringEngine.MODULE_WEIGHTS.get(vr.module_name, 10) * vr.confidence)
        elif vr.status == 'Unverifiable':
            pts = 5
            
        breakdown.append({
            "check": vr.module_name,
            "status": vr.status,
            "details": vr.details,
            "points_deducted": pts,
        })

    return {
        "appeal_id": appeal_id,
        "final_score": report.score,
        "summary": report.summary,
        "breakdown": breakdown,
        "evidence_graph": graph,
    }
