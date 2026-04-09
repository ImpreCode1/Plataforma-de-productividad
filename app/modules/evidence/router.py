from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.evidence import service
from app.modules.evidence.schemas import EvidenceResponse

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"]
)


# ------------------------------------------------
# UPLOAD (EMPLOYEE only)
# ------------------------------------------------

@router.post("/{tracking_id}", response_model=EvidenceResponse, dependencies=[Depends(require_roles("EMPLOYEE"))])
def upload_evidence(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    return service.create_evidence(db, tracking_id, file, current_user.id)


# ------------------------------------------------
# LIST (EMPLOYEE: own, LEADER: team, ADMIN: all)
# ------------------------------------------------

@router.get("/{tracking_id}")
def list_evidence(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    dependencies=[Depends(require_roles("EMPLOYEE", "LEADER", "ADMIN"))]
):
    service.check_access(db, tracking_id, current_user)
    data = service.list_evidence(db, tracking_id)
    return {"evidence": data}


# ------------------------------------------------
# DELETE (EMPLOYEE only, own evidence)
# ------------------------------------------------

@router.delete("/{evidence_id}")
def delete_evidence(
    evidence_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    dependencies=[Depends(require_roles("EMPLOYEE"))]
):
    service.check_evidence_ownership(db, evidence_id, current_user.id)
    service.delete_evidence(db, evidence_id)
    return {"message": "Deleted"}