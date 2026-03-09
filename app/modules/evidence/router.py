from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from db.session import get_db
from schemas import EvidenceCreate, EvidenceResponse
from service import EvidenceService

router = APIRouter(prefix="/evidences", tags=["Evidence"])


@router.post("/", response_model=EvidenceResponse)
def create_evidence(
    data: EvidenceCreate,
    db: Session = Depends(get_db)
):

    # luego se conecta con auth
    user_id = data.indicator_tracking_id

    return EvidenceService.create_evidence(db, data, user_id)


@router.get("/", response_model=list[EvidenceResponse])
def list_evidences(db: Session = Depends(get_db)):

    return EvidenceService.list_evidence(db)