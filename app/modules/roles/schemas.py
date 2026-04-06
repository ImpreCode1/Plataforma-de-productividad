from uuid import UUID
from pydantic import BaseModel
from typing import List


class RoleResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    roles: List[RoleResponse]


class CreateRoleRequest(BaseModel):
    name: str


class UpdateRoleRequest(BaseModel):
    name: str


# 🔥 CLAVE
class AssignRolesRequest(BaseModel):
    role_ids: List[UUID]