from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal


class IndicatorTrackingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    assignment_id: UUID

    year: int
    month: int

    achieved_value: Optional[Decimal]
    achievement_percentage: Optional[Decimal]
    weighted_score: Optional[Decimal]

    target_met: Optional[bool]
    status: Optional[str]
    is_closed: bool


class TrackingListResponse(BaseModel):
    tracking: List[IndicatorTrackingResponse]


class TrackingUpdateRequest(BaseModel):
    achieved_value: Decimal


class TrackingCloseRequest(BaseModel):
    pass