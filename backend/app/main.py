from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import time
import os

from app.core.database import get_db, engine
from app.models.evidence import Base, Appeal, ExtractedEntity, VerificationResult, TrustReport
from app.api.verification import router as verification_router
from app.services.extraction_layer import ExtractionLayer
from app.services.identity_module import IdentityModule
from app.services.payment_module import PaymentModule
from app.services.similarity_module import SimilarityModule
from app.services.claim_module import ClaimModule
from app.services.scoring_engine import ScoringEngine
from app.services.evidence_graph import EvidenceGraphBuilder

app = FastAPI(title="ReliefShield API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f} sec"
    return response

app.include_router(verification_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/api/v1/appeals/")
async def submit_appeal(
    input_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    url_link: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a new appeal, run the full verification pipeline, and return the trust report.
    """
    if input_type not in ["text", "link", "image"]:
        raise HTTPException(status_code=400, detail="Invalid input type. Must be 'text', 'link', or 'image'.")

    raw_content = ""
    image_bytes = None

    if input_type == "text" and text_content:
        raw_content = text_content
    elif input_type == "link" and url_link:
        raw_content = url_link
    elif input_type == "image" and image:
        image_bytes = await image.read()
        raw_content = image.filename
    else:
        raise HTTPException(status_code=400, detail="Content missing for the specified input type")

    # Step 1: Extraction
    extraction_result = ExtractionLayer.process_input(
        input_type, text_content=raw_content if input_type != "image" else None, image_bytes=image_bytes
    )
    full_text = extraction_result["raw_text"]
    entities = extraction_result["entities"]

    new_appeal = Appeal(
        input_type=input_type,
        raw_content=raw_content if input_type != "image" else full_text,
    )
    db.add(new_appeal)
    await db.commit()
    await db.refresh(new_appeal)

    for entity_type, values in entities.items():
        for val in values:
            db.add(ExtractedEntity(
                appeal_id=new_appeal.id,
                entity_type=entity_type,
                entity_value=val,
            ))
    await db.commit()

    # Step 2: Run Verification Modules
    org_name = ""
    if entities["ORG"]:
        for candidate in entities["ORG"]:
            check = IdentityModule.verify_organisation(candidate)
            if check["status"] == "Verified":
                org_name = candidate
                break
        if not org_name:
            org_name = max(entities["ORG"], key=len)
    payment_id = entities["PAYMENT_ID"][0] if entities["PAYMENT_ID"] else ""
    domains = entities["DOMAIN"]
    phones = entities.get("PHONE", [])
    banks = entities.get("BANK_INFO", [])

    verifications = []

    # Identity check
    id_result = IdentityModule.verify_organisation(org_name)
    if domains:
        domain_result = IdentityModule.verify_domain(domains[0])
        if domain_result["status"] == "Flagged":
            id_result = domain_result
    id_result["module_name"] = "Identity"
    verifications.append(id_result)

    # Payment check
    pay_result = PaymentModule.verify_payment_consistency(org_name, payment_id)
    pay_result["module_name"] = "Payment"
    verifications.append(pay_result)

    # Similarity check
    sim_result = SimilarityModule.verify_text_similarity(full_text)
    sim_result["module_name"] = "Similarity"
    verifications.append(sim_result)

    # Claim check
    claim_result = ClaimModule.verify_claims(full_text)
    claim_result["module_name"] = "Claim"
    verifications.append(claim_result)

    # Step 3: Build Evidence Graph
    graph = EvidenceGraphBuilder.build(
        appeal_text=full_text,
        org_name=org_name,
        payment_id=payment_id,
        domains=domains,
        phones=phones,
        banks=banks,
        verifications=verifications,
    )

    # Step 4: Score
    score_report = ScoringEngine.calculate_score(verifications)

    # Persist Verification Results
    for v in verifications:
        db.add(VerificationResult(
            appeal_id=new_appeal.id,
            module_name=v.get("module_name"),
            status=v.get("status"),
            confidence=v.get("confidence", 0.0),
            details=v.get("details", ""),
        ))

    # Persist Trust Report
    trust_report = TrustReport(
        appeal_id=new_appeal.id,
        score=score_report["final_score"],
        summary=score_report.get("summary", ""),
        evidence_graph=json.dumps(graph),
    )
    db.add(trust_report)
    await db.commit()

    return {
        "appeal_id": new_appeal.id,
        "final_score": score_report["final_score"],
        "risk_level": score_report.get("risk_level", "Unknown"),
        "summary": score_report.get("summary", ""),
        "recommendations": score_report.get("recommendations", []),
        "breakdown": score_report["breakdown"],
        "evidence_graph": graph,
        "extracted_entities": entities,
    }


# Static routing (for unified deployment)
@app.get("/")
def redirect_to_docs():
    return RedirectResponse("/docs")

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/app", StaticFiles(directory=frontend_dist, html=True), name="frontend")
