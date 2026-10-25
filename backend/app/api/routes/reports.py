"""
Report and Verification API Routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.report import Report, ReportVerification
from app.schemas.report import (
    ReportResponse,
    ReportVerificationRequest,
    ReportVerificationResponse
)
from app.services.verification.verifier import verification_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=List[ReportResponse])
def list_reports(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.generated_at.desc()).offset(skip).limit(limit).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report_by_id(report_id: str, db: Session = Depends(get_db)):
    rep = db.query(Report).filter(Report.id == report_id).first()
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found.")
    return rep


@router.post("/verify", response_model=ReportVerificationResponse)
async def verify_report(
    req: ReportVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Cryptographically verifies a report's SHA-256 hash against its canonical JSON representation.
    Optionally checks the on-chain InvestigationRegistry contract if requested.
    """
    res = await verification_service.verify(
        report_payload=req.report_payload,
        claimed_hash=req.expected_hash,
        check_chain=req.verify_on_chain
    )

    # If associated with a stored report, persist the verification event
    if req.report_id:
        db_rep = db.query(Report).filter(Report.id == req.report_id).first()
        if db_rep:
            ver_record = ReportVerification(
                id=f"ver-{uuid.uuid4().hex[:10]}" if 'uuid' in globals() else f"ver-{res.computed_hash[:8]}",
                report_id=db_rep.id,
                computed_hash=res.computed_hash,
                recorded_hash=res.claimed_hash,
                is_valid=res.is_valid,
                on_chain_checked=res.on_chain_checked,
                on_chain_verified=res.on_chain_verified,
                verification_details=res.model_dump()
            )
            db.add(ver_record)
            db.commit()

    return res
