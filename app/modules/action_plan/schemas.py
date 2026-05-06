from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class ActionPlanCreate(BaseModel):
    reason_not_met: str
    action_plan: str


class ActionPlanUpdate(BaseModel):
    reason_not_met: str | None = None
    action_plan: str | None = None


class ActionPlanResponse(BaseModel):
    id: UUID
    tracking_id: UUID
    reason_not_met: str
    action_plan: str
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True