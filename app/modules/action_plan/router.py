from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.action_plan.schemas import ActionPlanCreate, ActionPlanResponse
from app.modules.action_plan.service import ActionPlanService

router = APIRouter(prefix="/action-plans", tags=["Action Plans"])


@router.post("/", response_model=ActionPlanResponse)
def create_plan(
    data: ActionPlanCreate,
    db: Session = Depends(get_db)
):

    user_id = data.indicator_tracking_id

    return ActionPlanService.create_plan(db, data, user_id)


@router.get("/", response_model=list[ActionPlanResponse])
def list_plans(db: Session = Depends(get_db)):

    return ActionPlanService.list_plans(db)