from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Optional

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.indicator_assignments import service
from app.modules.indicator_assignments.schemas import (
    IndicatorAssignmentCreate,
    IndicatorAssignmentResponse,
    IndicatorAssignmentListResponse,
    IndicatorAssignmentUpdate,
    ImportAssignmentsResponse,
    ReopenAssignmentRequest
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
    month: int | None = None,
):
    if user_id and year:
        assignments = service.list_assignments(db, user_id, year, month)
    else:
        assignments = service.list_all_assignments(db, year, month)
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
    month: int | None = None,
    file: UploadFile = File(...)
):
    return service.import_assignments_from_excel(db, file.file, year, month)


# ------------------------------------------------
# CLOSE ASSIGNMENT
# ------------------------------------------------

@router.patch(
    "/{assignment_id}/close",
    response_model=IndicatorAssignmentResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def close_assignment(
    assignment_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    return service.close_assignment(db, assignment_id)


# ------------------------------------------------
# REOPEN ASSIGNMENT (create new with new position)
# ------------------------------------------------

@router.post(
    "/{assignment_id}/reopen",
    response_model=IndicatorAssignmentListResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def reopen_assignment(
    assignment_id: UUID,
    data: ReopenAssignmentRequest,
    db: DBSession,
    current_user: CurrentUser
):
    assignments = service.reopen_assignment(
        db, assignment_id, data.month, data.indicators
    )
    return {"assignments": [a for a, _ in assignments]}


# ------------------------------------------------
# CLONE FROM PREVIOUS MONTH
# ------------------------------------------------

@router.post(
    "/clone-previous-month",
    response_model=ImportAssignmentsResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def clone_from_previous_month(
    db: DBSession,
    current_user: CurrentUser,
    year: int,
    month: int
):
    return service.clone_from_previous_month(db, year, month)