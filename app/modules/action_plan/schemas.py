from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ActionPlanCreate(BaseModel):
    indicator_tracking_id: UUID
    reason_not_met: str
    action_plan: str


class ActionPlanUpdate(BaseModel):
    reason_not_met: str
    action_plan: str


class ActionPlanResponse(BaseModel):
    id: UUID
    indicator_tracking_id: UUID
    reason_not_met: str
    action_plan: str
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True