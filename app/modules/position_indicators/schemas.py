from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class PositionIndicatorBase(BaseModel):
    position_id: UUID
    indicator_id: UUID
    year: int
    target_value: float
    weight: float


class PositionIndicatorCreate(PositionIndicatorBase):
    pass


class PositionIndicatorUpdate(BaseModel):
    target_value: float | None = None
    weight: float | None = None


class PositionIndicatorResponse(PositionIndicatorBase):
    id: UUID

    class Config:
        from_attributes = True


class PositionIndicatorListResponse(BaseModel):
    position_indicators: list[PositionIndicatorResponse]