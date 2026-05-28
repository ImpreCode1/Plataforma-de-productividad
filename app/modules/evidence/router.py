from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Form, Depends, Query

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.evidence import service
from app.modules.evidence.schemas import EvidenceResponse, EvidenceListResponse, EvidenceUploadResponse, SetValueRequest
from app.modules.approval.schemas import TrackingApprovalResponse

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"]
)


# ------------------------------------------------
# UPLOAD TO ALL INDICATORS FOR MONTH (EMPLOYEE/LEADER/ADMIN) — LEGACY
# ------------------------------------------------

@router.post("/", response_model=EvidenceResponse, dependencies=[Depends(require_roles("EMPLOYEE", "LEADER", "ADMIN"))])
def upload_evidence_to_month(
    db: DBSession,
    current_user: CurrentUser,
    year: int = Form(...),
    month: int = Form(...),
    target_user_id: UUID = Form(None),
    file: UploadFile = File(...)
):
    user_id = target_user_id or current_user.id
    return service.create_evidence(db, file, current_user.id, year=year, month=month, target_user_id=user_id)


# ------------------------------------------------
# UPLOAD EVIDENCE PER TRACKING (NEW)
# ------------------------------------------------

@router.post(
    "/tracking/{tracking_id}",
    response_model=EvidenceUploadResponse,
)
def upload_evidence_to_tracking(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    return service.create_evidence_for_tracking(db, file, str(tracking_id), current_user)


# ------------------------------------------------
# SET VALUE PER ASSIGNMENT (auto-creates tracking)
# ------------------------------------------------

@router.patch(
    "/assignment/{assignment_id}/value",
    response_model=TrackingApprovalResponse,
)
def set_tracking_value(
    assignment_id: UUID,
    data: SetValueRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    return service.set_assignment_value(db, assignment_id, data.achieved_value, data.achieved_total, current_user)


# ------------------------------------------------
# UPLOAD EVIDENCE PER ASSIGNMENT (auto-creates tracking)
# ------------------------------------------------

@router.post(
    "/assignment/{assignment_id}",
    response_model=EvidenceUploadResponse,
)
def upload_evidence_to_assignment(
    assignment_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    return service.create_evidence_for_assignment(db, file, assignment_id, current_user)


# ------------------------------------------------
# LIST BY MONTH (EMPLOYEE: own, LEADER: team, ADMIN: all)
# ------------------------------------------------

@router.get("/", response_model=EvidenceListResponse, dependencies=[Depends(require_roles("EMPLOYEE", "LEADER", "ADMIN"))])
def list_evidences_by_month(
    db: DBSession,
    current_user: CurrentUser,
    year: int = Query(...),
    month: int = Query(...),
    target_user_id: UUID = Query(None),
):
    user_id = target_user_id or current_user.id
    evidences = service.list_evidences_by_month(db, user_id, year, month)
    return {"evidences": evidences}


# ------------------------------------------------
# LIST BY TRACKING (EMPLOYEE: own, LEADER: team, ADMIN: all)
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