from uuid import UUID
from datetime import date
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


# -----------------------------
# RESPONSE
# -----------------------------

class RoleOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: UUID
    document_number: str
    name: str
    email: EmailStr

    position_name: Optional[str]
    area: Optional[str]
    subarea: Optional[str]

    hire_date: Optional[date]
    contract_type: Optional[str]
    salary_type: Optional[str]

    leader_id: Optional[UUID]
    is_active: bool

    roles: List[RoleOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]


# -----------------------------
# REQUESTS
# -----------------------------

class ChangeStatusRequest(BaseModel):
    is_active: bool


class AssignLeaderRequest(BaseModel):
    leader_id: Optional[UUID]


class ImportExcelResponse(BaseModel):
    created: int
    updated: int