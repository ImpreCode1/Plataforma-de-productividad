from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.core.security.dependencies import CurrentUser
from app.modules.evidence.schemas import (
    EvidenceCreate, 
    EvidenceResponse,
    EvidenceReviewRequest,
    EvidenceReviewResponse
)
from app.modules.evidence.service import EvidenceService

router = APIRouter(prefix="/evidences", tags=["Evidence"])


@router.post("/", response_model=EvidenceResponse)
def create_evidence(data: EvidenceCreate, current_user: CurrentUser, db: Session = Depends(get_db)):

    return EvidenceService.create_evidence(db, data, current_user.id)


@router.get("/", response_model=list[EvidenceResponse])
def list_evidences(db: Session = Depends(get_db)):

    return EvidenceService.list_evidences(db)


@router.get("/my-evidences", response_model=list[EvidenceResponse])
def list_my_evidences(current_user: CurrentUser, db: Session = Depends(get_db)):

    return EvidenceService.list_user_evidences(db, current_user.id)


@router.get("/team-evidences", response_model=list[EvidenceResponse])
def list_team_evidences(current_user: CurrentUser, db: Session = Depends(get_db)):

    return EvidenceService.list_team_evidences(db, current_user.id)


@router.get("/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(evidence_id: UUID, db: Session = Depends(get_db)):

    return EvidenceService.get_evidence(db, evidence_id)


@router.patch("/{evidence_id}/review", response_model=EvidenceReviewResponse)
def review_evidence(
    evidence_id: UUID, 
    data: EvidenceReviewRequest, 
    current_user: CurrentUser, 
    db: Session = Depends(get_db)
):

    if data.status not in ["approved", "rejected"]:
        raise APIRouter.HTTPException(status_code=400, detail="Status must be approved or rejected")

    return EvidenceService.review_evidence(db, evidence_id, current_user.id, data.status)


@router.delete("/{evidence_id}")
def delete_evidence(evidence_id: UUID, db: Session = Depends(get_db)):

    return EvidenceService.delete_evidence(db, evidence_id)