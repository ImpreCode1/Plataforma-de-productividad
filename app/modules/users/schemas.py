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
    direccion: Optional[str] = None
    linea: Optional[str] = None
    numero_linea: Optional[str] = None

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


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    document_number: Optional[str] = None
    position_name: Optional[str] = None
    area: Optional[str] = None
    subarea: Optional[str] = None
    direccion: Optional[str] = None
    linea: Optional[str] = None
    numero_linea: Optional[str] = None


class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    document_number: str
    position_name: Optional[str] = None
    area: Optional[str] = None
    subarea: Optional[str] = None
    direccion: Optional[str] = None
    linea: Optional[str] = None
    numero_linea: Optional[str] = None


class ImportExcelResponse(BaseModel):
    created: int
    updated: int