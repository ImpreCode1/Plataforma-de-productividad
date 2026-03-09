from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.position_indicators import service
from app.modules.position_indicators.schemas import (
    PositionIndicatorCreate,
    PositionIndicatorUpdate,
    PositionIndicatorResponse,
    PositionIndicatorListResponse
)

router = APIRouter(
    prefix="/position-indicators",
    tags=["Position Indicators"]
)


# -----------------------------------------
# List
# -----------------------------------------

@router.get(
    "/",
    response_model=PositionIndicatorListResponse
)
def list_position_indicators(
    db: DBSession,
    current_user: CurrentUser
):

    pis = service.get_position_indicators(db)

    return {
        "position_indicators": pis
    }


# -----------------------------------------
# Get
# -----------------------------------------

@router.get(
    "/{pi_id}",
    response_model=PositionIndicatorResponse
)
def get_position_indicator(
    pi_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):

    return service.get_position_indicator(db, pi_id)


# -----------------------------------------
# Create
# -----------------------------------------

@router.post(
    "/",
    response_model=PositionIndicatorResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def create_position_indicator(
    data: PositionIndicatorCreate,
    db: DBSession,
    current_user: CurrentUser
):

    return service.create_position_indicator(db, data)


# -----------------------------------------
# Update
# -----------------------------------------

@router.patch(
    "/{pi_id}",
    response_model=PositionIndicatorResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def update_position_indicator(
    pi_id: UUID,
    data: PositionIndicatorUpdate,
    db: DBSession,
    current_user: CurrentUser
):

    return service.update_position_indicator(db, pi_id, data)


# -----------------------------------------
# Delete
# -----------------------------------------

@router.delete(
    "/{pi_id}",
    response_model=PositionIndicatorResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def delete_position_indicator(
    pi_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):

    return service.delete_position_indicator(db, pi_id)