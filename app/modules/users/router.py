from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.modules.users import service
from app.modules.users.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    ChangeStatusRequest,
    AssignLeaderRequest,
    AssignRolesRequest,
    ChangePositionRequest
)
from app.core.security.dependencies import (
    get_current_user,
    require_roles,
)

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/status")
def state():
    return {"message": "Users endpoint working"}

@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    return service.get_user_by_id(db, user_id)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_endpoint(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    return service.create_user(db, payload)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service.deactivate_user(db, user_id)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.get_user(db, user_id)


@router.patch("/{user_id}/status", response_model=UserResponse)
def change_status(
    user_id: UUID,
    payload: ChangeStatusRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.change_status(db, user_id, payload.is_active)


@router.patch("/{user_id}/roles", response_model=UserResponse)
def assign_roles(
    user_id: UUID,
    payload: AssignRolesRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.assign_roles(db, user_id, payload.role_ids)


@router.patch("/{user_id}/leader", response_model=UserResponse)
def assign_leader(
    user_id: UUID,
    payload: AssignLeaderRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.assign_leader(db, user_id, payload.leader_id)


@router.patch("/{user_id}/position", response_model=UserResponse)
def change_position(
    user_id: UUID,
    payload: ChangePositionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.change_position(db, user_id, payload.position_id)