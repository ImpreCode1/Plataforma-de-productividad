from pydantic import BaseModel, EmailStr, model_serializer
from uuid import UUID
from typing import List, Optional


# -----------------------------
# Base
# -----------------------------

class UserBase(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    is_active: bool
    position_id: Optional[UUID]
    leader_id: Optional[UUID]


# -----------------------------
# Position Response
# -----------------------------

class PositionResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


# -----------------------------
# User Response
# -----------------------------

class UserResponse(UserBase):
    roles: List[str] = []
    position: Optional[PositionResponse] = None
    leader_name: Optional[str] = None

    class Config:
        from_attributes = True


# -----------------------------
# List Response
# -----------------------------

class UserListResponse(BaseModel):
    users: List[UserResponse]


# -----------------------------
# Requests
# -----------------------------

class ChangeStatusRequest(BaseModel):
    is_active: bool


class AssignRolesRequest(BaseModel):
    role_ids: List[UUID]


class AssignLeaderRequest(BaseModel):
    leader_id: Optional[UUID]


class ChangePositionRequest(BaseModel):
    position_id: Optional[UUID]