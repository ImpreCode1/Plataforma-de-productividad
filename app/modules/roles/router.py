from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.modules.roles.schemas import RoleCreate, RoleUpdate, RoleResponse
from app.modules.roles.service import RoleService

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.get("/", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):

    return RoleService.list_roles(db)


@router.post("/", response_model=RoleResponse)
def create_role(data: RoleCreate, db: Session = Depends(get_db)):

    return RoleService.create_role(db, data)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(role_id: UUID, db: Session = Depends(get_db)):

    return RoleService.get_role(db, role_id)


@router.patch("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: UUID,
    data: RoleUpdate,
    db: Session = Depends(get_db)
):

    return RoleService.update_role(db, role_id, data)


@router.delete("/{role_id}")
def delete_role(role_id: UUID, db: Session = Depends(get_db)):

    return RoleService.delete_role(db, role_id)