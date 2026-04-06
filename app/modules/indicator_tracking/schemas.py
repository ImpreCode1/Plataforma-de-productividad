from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


# -----------------------------
# RESPONSE
# -----------------------------

class IndicatorTrackingResponse(BaseModel):
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

    class Config:
        from_attributes = True


# -----------------------------
# REQUESTS
# -----------------------------

class TrackingUpdateRequest(BaseModel):
    achieved_value: Decimal


class TrackingCloseRequest(BaseModel):
    pass