from uuid import UUID
from fastapi import APIRouter, UploadFile, File

from app.core.security.dependencies import DBSession, CurrentUser
from app.modules.evidence import service
from app.modules.evidence.schemas import EvidenceResponse

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"]
)


# ------------------------------------------------
# UPLOAD
# ------------------------------------------------

@router.post("/{tracking_id}", response_model=EvidenceResponse)
def upload_evidence(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    return service.create_evidence(db, tracking_id, file, current_user.id)


# ------------------------------------------------
# LIST
# ------------------------------------------------

@router.get("/{tracking_id}")
def list_evidence(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    data = service.list_evidence(db, tracking_id)
    return {"evidence": data}


# ------------------------------------------------
# DELETE
# ------------------------------------------------

@router.delete("/{evidence_id}")
def delete_evidence(
    evidence_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    service.delete_evidence(db, evidence_id)
    return {"message": "Deleted"}