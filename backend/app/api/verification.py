from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import json

from app.core.database import get_db
from app.models.evidence import Appeal, TrustReport, VerificationResult
from app.services.extraction_layer import ExtractionLayer
from app.services.identity_module import IdentityModule
from app.services.payment_module import PaymentModule
from app.services.similarity_module import SimilarityModule
from app.services.claim_module import ClaimModule
from app.services.scoring_engine import ScoringEngine
from app.services.evidence_graph import EvidenceGraphBuilder
from pydantic import BaseModel

router = APIRouter()


class VerifyRequest(BaseModel):
    appeal_id: int
    text_content: str = ""


@router.post("/verify")
async def run_verification_pipeline(req: VerifyRequest, db: AsyncSession = Depends(get_db)):
    """
    Run the full verification pipeline on provided text.
    """
    extraction_result = ExtractionLayer.process_input("text", text_content=req.text_content)
    entities = extraction_result["entities"]
    full_text = extraction_result["raw_text"]

    org_name = entities["ORG"][0] if entities["ORG"] else ""
    payment_id = entities["PAYMENT_ID"][0] if entities["PAYMENT_ID"] else ""
    domains = entities.get("DOMAIN", [])

    verifications = []

    id_result = IdentityModule.verify_organisation(org_name)
    if domains:
        domain_result = IdentityModule.verify_domain(domains[0])
        if domain_result["status"] == "Flagged":
            id_result = domain_result
    id_result["module_name"] = "Identity"
    verifications.append(id_result)

    pay_result = PaymentModule.verify_payment_consistency(org_name, payment_id)
    pay_result["module_name"] = "Payment"
    verifications.append(pay_result)

    sim_result = SimilarityModule.verify_text_similarity(req.text_content)
    sim_result["module_name"] = "Similarity"
    verifications.append(sim_result)

    claim_result = ClaimModule.verify_claims(req.text_content)
    claim_result["module_name"] = "Claim"
    verifications.append(claim_result)

    graph = EvidenceGraphBuilder.build(
        appeal_text=full_text,
        org_name=org_name,
        payment_id=payment_id,
        domains=domains,
        verifications=verifications,
    )

    score_report = ScoringEngine.calculate_score(verifications)

    for v in verifications:
        db.add(VerificationResult(
            appeal_id=req.appeal_id,
            module_name=v.get("module_name"),
            status=v.get("status"),
            confidence=v.get("confidence", 0.0),
            details=v.get("details", ""),
        ))

    trust_report = TrustReport(
        appeal_id=req.appeal_id,
        score=score_report["final_score"],
        summary=score_report.get("summary", ""),
        evidence_graph=json.dumps(graph),
    )
    db.add(trust_report)
    await db.commit()

    return {
        "appeal_id": req.appeal_id,
        "final_score": score_report["final_score"],
        "summary": score_report.get("summary", ""),
        "breakdown": score_report["breakdown"],
        "evidence_graph": graph,
        "extracted_entities": entities,
    }


@router.get("/reports/{appeal_id}")
async def get_report(appeal_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetch a previously generated trust report by appeal ID.
    """
    result = await db.execute(select(TrustReport).where(TrustReport.appeal_id == appeal_id))
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this appeal.")

    graph = json.loads(report.evidence_graph) if report.evidence_graph else {}

    ver_result = await db.execute(
        select(VerificationResult).where(VerificationResult.appeal_id == appeal_id)
    )
    ver_records = ver_result.scalars().all()
    breakdown = [
        {
            "check": vr.module_name,
            "status": vr.status,
            "details": vr.details,
            "points_deducted": 0,
        }
        for vr in ver_records
    ]

    return {
        "appeal_id": appeal_id,
        "final_score": report.score,
        "summary": report.summary,
        "breakdown": breakdown,
        "evidence_graph": graph,
    }
