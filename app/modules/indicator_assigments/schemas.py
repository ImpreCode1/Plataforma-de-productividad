from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


# ---------------------------------
# Base
# ---------------------------------

class IndicatorBase(BaseModel):
    name: str
    formula_text: str | None = None
    frequency: str


# ---------------------------------
# Create
# ---------------------------------

class IndicatorCreate(IndicatorBase):
    pass


# ---------------------------------
# Update
# ---------------------------------

class IndicatorUpdate(BaseModel):
    name: str | None = None
    formula_text: str | None = None
    frequency: str | None = None
    is_active: bool | None = None


# ---------------------------------
# Response
# ---------------------------------

class IndicatorResponse(IndicatorBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------
# List Response
# ---------------------------------

class IndicatorListResponse(BaseModel):
    indicators: list[IndicatorResponse]