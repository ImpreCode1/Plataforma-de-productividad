from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class OrganizationUnitBase(BaseModel):
    name: str
    type: str
    parent_id: UUID | None = None


class OrganizationUnitCreate(OrganizationUnitBase):
    pass


class OrganizationUnitUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    parent_id: UUID | None = None


class OrganizationUnitResponse(OrganizationUnitBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationUnitListResponse(BaseModel):
    units: list[OrganizationUnitResponse]