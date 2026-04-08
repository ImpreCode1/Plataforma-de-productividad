from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.indicator_assignments import service
from app.modules.indicator_assignments.schemas import (
    IndicatorAssignmentCreate,
    IndicatorAssignmentResponse,
    IndicatorAssignmentListResponse,
    IndicatorAssignmentUpdate,
    ImportAssignmentsResponse
)

router = APIRouter(
    prefix="/assignments",
    tags=["Indicator Assignments"]
)


# ------------------------------------------------
# CREATE
# ------------------------------------------------

@router.post(
    "/",
    response_model=IndicatorAssignmentResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def create_assignment(
    data: IndicatorAssignmentCreate,
    db: DBSession,
    current_user: CurrentUser
):
    return service.create_assignment(db, data)


# ------------------------------------------------
# LIST (all or filtered)
# ------------------------------------------------

@router.get(
    "/",
    response_model=IndicatorAssignmentListResponse
)
def list_assignments(
    db: DBSession,
    current_user: CurrentUser,
    user_id: UUID | None = None,
    year: int | None = None,
):
    if user_id and year:
        assignments = service.list_assignments(db, user_id, year)
    else:
        assignments = service.list_all_assignments(db, year)
    return {"assignments": assignments}


# ------------------------------------------------
# UPDATE
# ------------------------------------------------

@router.patch(
    "/{assignment_id}",
    response_model=IndicatorAssignmentResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def update_assignment(
    assignment_id: UUID,
    data: IndicatorAssignmentUpdate,
    db: DBSession,
    current_user: CurrentUser
):
    return service.update_assignment(db, assignment_id, data)


# ------------------------------------------------
# DELETE
# ------------------------------------------------

@router.delete(
    "/{assignment_id}",
    dependencies=[Depends(require_roles("ADMIN"))]
)
def delete_assignment(
    assignment_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    service.delete_assignment(db, assignment_id)
    return {"message": "Deleted successfully"}


# ------------------------------------------------
# IMPORT EXCEL 🔥
# ------------------------------------------------

@router.post(
    "/import-excel",
    response_model=ImportAssignmentsResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def import_assignments(
    db: DBSession,
    current_user: CurrentUser,
    year: int,
    file: UploadFile = File(...)
):
    return service.import_assignments_from_excel(db, file.file, year)