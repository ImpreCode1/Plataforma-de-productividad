from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


# -----------------------------
# Base
# -----------------------------


class PositionBase(BaseModel):
    name: str
    description: str | None = None


# -----------------------------
# Create
# -----------------------------


class PositionCreate(PositionBase):
    pass


# -----------------------------
# Update
# -----------------------------


class PositionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


# -----------------------------
# Response
# -----------------------------


class PositionResponse(PositionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# List Response
# -----------------------------


class PositionListResponse(BaseModel):
    positions: list[PositionResponse]
