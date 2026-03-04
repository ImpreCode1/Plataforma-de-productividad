from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    external_auth_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=150)
    email: str = Field(min_length=5, max_length=255)
    position_id: UUID | None = None
    leader_id: UUID | None = None
    is_active: bool = True


class UserUpdate(BaseModel):
    external_auth_id: str | None = Field(default=None, min_length=1, max_length=255)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: str | None = Field(default=None, min_length=5, max_length=255)
    position_id: UUID | None = None
    leader_id: UUID | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_auth_id: str
    name: str
    email: str = Field(min_length=5, max_length=255)
    position_id: UUID | None
    leader_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
class AssignRolesRequest(BaseModel):
    role_ids: List[UUID]


class AssignLeaderRequest(BaseModel):
    leader_id: UUID | None


class ChangePositionRequest(BaseModel):
    position_id: UUID | None


class ChangeStatusRequest(BaseModel):
    is_active: bool