from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.modules.evidence.schemas import EvidenceCreate, EvidenceResponse
from app.modules.evidence.service import EvidenceService

router = APIRouter(prefix="/evidences", tags=["Evidence"])


@router.post("/", response_model=EvidenceResponse)
def create_evidence(data: EvidenceCreate, db: Session = Depends(get_db)):

    user_id = data.indicator_tracking_id

    return EvidenceService.create_evidence(db, data, user_id)


@router.get("/", response_model=list[EvidenceResponse])
def list_evidences(db: Session = Depends(get_db)):

    return EvidenceService.list_evidences(db)


@router.get("/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(evidence_id: UUID, db: Session = Depends(get_db)):

    return EvidenceService.get_evidence(db, evidence_id)


@router.delete("/{evidence_id}")
def delete_evidence(evidence_id: UUID, db: Session = Depends(get_db)):

    return EvidenceService.delete_evidence(db, evidence_id)