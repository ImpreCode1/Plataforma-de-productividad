from uuid import UUID
from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    document_number: str
    name: str
    email: EmailStr

    position_name: Optional[str] = None
    area: Optional[str] = None
    subarea: Optional[str] = None

    hire_date: Optional[date] = None
    contract_type: Optional[str] = None
    salary_type: Optional[str] = None

    leader_id: Optional[UUID] = None
    is_active: bool = True
    roles: List[RoleOut] = Field(default_factory=list)


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