from pydantic import BaseModel
from uuid import UUID


class RoleCreate(BaseModel):

    name: str
    description: str


class RoleUpdate(BaseModel):

    name: str
    description: str


class RoleResponse(BaseModel):

    id: UUID
    name: str
    description: str

    class Config:
        from_attributes = True