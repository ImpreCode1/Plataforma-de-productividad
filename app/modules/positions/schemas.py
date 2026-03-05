from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class PositionBase(BaseModel):
    name: str
    organization_unit_id: UUID

class PositionCreate(PositionBase):
    pass

class PositionUpdate(BaseModel):
    name: Optional[str] = None
    organization_unit_id: Optional[UUID] = None

class PositionResponse(PositionBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True