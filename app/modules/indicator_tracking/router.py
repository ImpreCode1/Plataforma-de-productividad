from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.indicator_tracking import service
from app.modules.indicator_tracking.schemas import (
    IndicatorTrackingResponse,
    TrackingUpdateRequest
)

router = APIRouter(
    prefix="/tracking",
    tags=["Indicator Tracking"]
)


# ------------------------------------------------
# GET TRACKING BY USER
# ------------------------------------------------

@router.get("/")
def get_tracking(
    user_id: UUID,
    year: int,
    db: DBSession,
    current_user: CurrentUser
):
    data = service.get_tracking_by_user(db, user_id, year)
    return {"tracking": data}


# ------------------------------------------------
# GET ONE
# ------------------------------------------------

@router.get("/{tracking_id}", response_model=IndicatorTrackingResponse)
def get_one(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    return service.get_tracking(db, tracking_id)


# ------------------------------------------------
# UPDATE (USER REPORT)
# ------------------------------------------------

@router.patch(
    "/{tracking_id}",
    response_model=IndicatorTrackingResponse
)
def update_tracking(
    tracking_id: UUID,
    data: TrackingUpdateRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return service.update_tracking(db, tracking_id, data.achieved_value)


# ------------------------------------------------
# CLOSE (LEADER)
# ------------------------------------------------

@router.patch(
    "/{tracking_id}/close",
    response_model=IndicatorTrackingResponse,
    dependencies=[Depends(require_roles("LEADER", "ADMIN"))]
)
def close_tracking(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    return service.close_tracking(db, tracking_id)