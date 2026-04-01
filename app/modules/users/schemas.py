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
# Response
# -----------------------------

class UserResponse(UserBase):
    roles: List[str] = []

    @model_serializer(mode='wrap')
    def serialize_roles(self, handler):
        data = handler(self)
        if hasattr(self, 'user_roles'):
            roles = []
            for ur in self.user_roles:
                if hasattr(ur, 'role') and ur.role:
                    roles.append(ur.role.name)
                elif hasattr(ur, 'name'):
                    roles.append(ur.name)
            data['roles'] = roles
        return data

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