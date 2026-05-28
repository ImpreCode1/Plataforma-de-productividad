from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.approval import service
from app.modules.approval.schemas import (
    TrackingApproveRequest,
    TrackingRejectRequest,
    TrackingApprovalResponse,
)

router = APIRouter(
    prefix="/tracking",
    tags=["Approval"],
)


@router.patch(
    "/{tracking_id}/submit",
    response_model=TrackingApprovalResponse,
)
def submit_tracking(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    return service.submit_tracking(db, tracking_id, current_user)


@router.post(
    "/assignment/{assignment_id}/submit",
    response_model=TrackingApprovalResponse,
)
def submit_assignment(
    assignment_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    return service.submit_assignment(db, assignment_id, current_user)


@router.patch(
    "/{tracking_id}/approve",
    response_model=TrackingApprovalResponse,
    dependencies=[Depends(require_roles("LEADER", "ADMIN"))],
)
def approve_tracking(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    return service.approve_tracking(db, tracking_id, current_user)


@router.patch(
    "/{tracking_id}/reject",
    response_model=TrackingApprovalResponse,
    dependencies=[Depends(require_roles("LEADER", "ADMIN"))],
)
def reject_tracking(
    tracking_id: UUID,
    data: TrackingRejectRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    return service.reject_tracking(db, tracking_id, current_user, data.comment)
