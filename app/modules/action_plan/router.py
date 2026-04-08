from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.security.dependencies import DBSession, CurrentUser
from app.modules.action_plan import service
from app.modules.action_plan.schemas import (
    ActionPlanCreate,
    ActionPlanResponse,
    ActionPlanUpdate
)

router = APIRouter(
    prefix="/action-plan",
    tags=["Action Plan"]
)

class ActionPlanListResponse(BaseModel):
    action_plans: list


# ------------------------------------------------
# LIST ALL (Leader's Team)
# ------------------------------------------------

@router.get("/team/{leader_id}/{year}", response_model=ActionPlanListResponse)
def list_team_action_plans(
    leader_id: UUID,
    year: int,
    db: DBSession,
    current_user: CurrentUser
):
    data = service.list_team_action_plans(db, leader_id, year)
    return {"action_plans": data}


# ------------------------------------------------
# CREATE
# ------------------------------------------------

@router.post("/{tracking_id}", response_model=ActionPlanResponse)
def create_action_plan(
    tracking_id: UUID,
    data: ActionPlanCreate,
    db: DBSession,
    current_user: CurrentUser
):
    return service.create_action_plan(db, tracking_id, data, current_user.id)


# ------------------------------------------------
# LIST
# ------------------------------------------------

@router.get("/{tracking_id}")
def list_action_plans(
    tracking_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    data = service.list_action_plans(db, tracking_id)
    return {"action_plans": data}


# ------------------------------------------------
# UPDATE
# ------------------------------------------------

@router.patch("/{action_plan_id}", response_model=ActionPlanResponse)
def update_action_plan(
    action_plan_id: UUID,
    data: ActionPlanUpdate,
    db: DBSession,
    current_user: CurrentUser
):
    return service.update_action_plan(db, action_plan_id, data)