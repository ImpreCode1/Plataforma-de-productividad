from uuid import UUID
from pydantic import BaseModel
from typing import List
from decimal import Decimal


class IndicatorAssignmentCreate(BaseModel):
    user_id: UUID
    indicator_name: str
    year: int
    target_value: Decimal
    weight: Decimal


class IndicatorAssignmentUpdate(BaseModel):
    indicator_name: str | None = None
    target_value: Decimal | None = None
    weight: Decimal | None = None
    is_active: bool | None = None


class IndicatorAssignmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    indicator_name: str
    year: int
    target_value: Decimal
    weight: Decimal
    is_active: bool

    class Config:
        from_attributes = True


class IndicatorAssignmentListResponse(BaseModel):
    assignments: List[IndicatorAssignmentResponse]