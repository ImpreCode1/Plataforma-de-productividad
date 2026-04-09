from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Depends, Query

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.evidence import service
from app.modules.evidence.schemas import EvidenceResponse

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"]
)


# ------------------------------------------------
# UPLOAD TO ALL INDICATORS FOR MONTH (EMPLOYEE/LEADER/ADMIN)
# ------------------------------------------------

@router.post("/", response_model=EvidenceResponse, dependencies=[Depends(require_roles("EMPLOYEE", "LEADER", "ADMIN"))])
def upload_evidence_to_month(
    db: DBSession,
    current_user: CurrentUser,
    year: int = Query(...),
    month: int = Query(...),
    target_user_id: UUID = Query(None),
    file: UploadFile = File(...)
):
    user_id = target_user_id or current_user.id
    return service.create_evidence(db, file, current_user.id, year=year, month=month, target_user_id=user_id)


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