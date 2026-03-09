from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.indicators import service
from app.modules.indicators.schemas import (
    IndicatorCreate,
    IndicatorUpdate,
    IndicatorResponse,
    IndicatorListResponse
)

router = APIRouter(
    prefix="/indicators",
    tags=["Indicators"]
)


# ---------------------------------
# List indicators
# ---------------------------------

@router.get(
    "/",
    response_model=IndicatorListResponse
)
def list_indicators(
    db: DBSession,
    current_user: CurrentUser
):

    indicators = service.get_indicators(db)

    return {
        "indicators": indicators
    }


# ---------------------------------
# Get indicator
# ---------------------------------

@router.get(
    "/{indicator_id}",
    response_model=IndicatorResponse
)
def get_indicator(
    indicator_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):

    return service.get_indicator(db, indicator_id)


# ---------------------------------
# Create indicator
# ---------------------------------

@router.post(
    "/",
    response_model=IndicatorResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def create_indicator(
    data: IndicatorCreate,
    db: DBSession,
    current_user: CurrentUser
):

    return service.create_indicator(db, data)


# ---------------------------------
# Update indicator
# ---------------------------------

@router.patch(
    "/{indicator_id}",
    response_model=IndicatorResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def update_indicator(
    indicator_id: UUID,
    data: IndicatorUpdate,
    db: DBSession,
    current_user: CurrentUser
):

    return service.update_indicator(db, indicator_id, data)


# ---------------------------------
# Delete indicator
# ---------------------------------

@router.delete(
    "/{indicator_id}",
    response_model=IndicatorResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def delete_indicator(
    indicator_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):

    return service.delete_indicator(db, indicator_id)