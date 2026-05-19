from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.users import service
from app.modules.users.schemas import (
    UserResponse,
    UserListResponse,
    ChangeStatusRequest,
    AssignLeaderRequest,
    UpdateUserRequest,
    CreateUserRequest,
    ImportExcelResponse
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ------------------------------------------------
# Get unique areas (Vicepresidencias)
# ------------------------------------------------

@router.get(
    "/areas",
    response_model=list[str]
)
def get_areas(
    db: DBSession,
    current_user: CurrentUser
):
    return service.get_unique_areas(db)


# ------------------------------------------------
# List users
# ------------------------------------------------

@router.get(
    "/",
    response_model=UserListResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def list_users(
    db: DBSession,
    current_user: CurrentUser
):
    users = service.list_users(db)
    return {"users": users}


# ------------------------------------------------
# Get current user (me)
# ------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    db: DBSession,
    current_user: CurrentUser
):
    return service.get_user_with_roles(db, current_user.id)


# ------------------------------------------------
# Get user detail
# ------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    return service.get_user_with_roles(db, user_id)


# ------------------------------------------------
# Activate / deactivate
# ------------------------------------------------

@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def change_status(
    user_id: UUID,
    data: ChangeStatusRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return service.change_status(db, user_id, data.is_active)


# ------------------------------------------------
# Assign leader
# ------------------------------------------------

@router.patch(
    "/{user_id}/leader",
    response_model=UserResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def assign_leader(
    user_id: UUID,
    data: AssignLeaderRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return service.assign_leader(db, user_id, data.leader_id)


# ------------------------------------------------
# Update user
# ------------------------------------------------

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def update_user(
    user_id: UUID,
    data: UpdateUserRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return service.update_user(db, user_id, data.model_dump(exclude_unset=True))


# ------------------------------------------------
# CREATE USER
# ------------------------------------------------

@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def create_user(
    data: CreateUserRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return service.create_user(db, data)


# ------------------------------------------------
# IMPORT EXCEL 🔥
# ------------------------------------------------

@router.post(
    "/import-excel",
    response_model=ImportExcelResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def import_excel(
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    return service.import_users_from_excel(db, file.file)