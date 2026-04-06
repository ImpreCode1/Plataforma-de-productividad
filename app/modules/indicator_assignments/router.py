from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.indicator_assignments import service
from app.modules.indicator_assignments.schemas import (
    IndicatorAssignmentCreate,
    IndicatorAssignmentResponse,
    IndicatorAssignmentListResponse,
    IndicatorAssignmentUpdate
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
# LIST
# ------------------------------------------------

@router.get(
    "/",
    response_model=IndicatorAssignmentListResponse
)
def list_assignments(
    user_id: UUID,
    year: int,
    db: DBSession,
    current_user: CurrentUser
):
    assignments = service.list_assignments(db, user_id, year)
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