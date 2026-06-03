from uuid import UUID
from fastapi import APIRouter, Depends, Path, Query

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.indicator_tracking import service
from app.modules.indicator_tracking.schemas import (
    IndicatorTrackingResponse,
    TrackingUpdateRequest,
    TrackingCloseRequest,
    TrackingListResponse
)

router = APIRouter(
    prefix="/tracking",
    tags=["Indicator Tracking"]
)


# ------------------------------------------------
# GET MY TRACKING
# ------------------------------------------------

@router.get("/me", response_model=TrackingListResponse)
def get_my_tracking(
    year: int = Query(default=..., description="Año de seguimiento"),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    data = service.get_tracking_by_user(db, current_user.id, year)
    return {"tracking": data}


# ------------------------------------------------
# GET TRACKING BY USER
# ------------------------------------------------

@router.get("/", response_model=TrackingListResponse)
def get_tracking(
    user_id: UUID,
    year: int,
    db: DBSession,
    current_user: CurrentUser
):
    data = service.get_tracking_by_user(db, user_id, year)
    return {"tracking": data}


# ------------------------------------------------
# GET MY TEAM TRACKING (LEADER)
# ------------------------------------------------

@router.get("/team/{year}", response_model=TrackingListResponse)
def get_team_tracking(
    year: int = Path(default=..., description="Año de seguimiento"),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    data = service.get_team_tracking(db, current_user.id, year)
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
    return service.update_tracking(db, tracking_id, data.achieved_value, data.achieved_total)


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
    data: TrackingCloseRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return service.close_tracking(db, tracking_id, data.achieved_value, data.achieved_total, approved_by=current_user.id)


# ------------------------------------------------
# CLOSE ASSIGNMENT DIRECTLY (NEW MODEL)
# ------------------------------------------------

@router.patch(
    "/assignment/{assignment_id}/close",
    response_model=IndicatorTrackingResponse,
    dependencies=[Depends(require_roles("LEADER", "ADMIN"))]
)
def close_assignment_directly(
    assignment_id: UUID,
    data: TrackingCloseRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return service.close_assignment_direct(db, assignment_id, data.achieved_value, data.achieved_total, current_user.id)