from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class IndicatorTrackingCreate(BaseModel):
    user_id: UUID
    position_indicator_id: UUID
    month: int
    achieved_value: float


class IndicatorTrackingUpdate(BaseModel):
    achieved_value: float


class IndicatorTrackingResponse(BaseModel):
    id: UUID
    user_id: UUID
    position_indicator_id: UUID
    month: int
    achieved_value: float
    achievement_percentage: float
    weighted_score: float
    target_met: bool
    status: str
    created_at: datetime

    class Config:
        orm_mode = True