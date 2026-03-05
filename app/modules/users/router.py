from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.users import service
from app.modules.users.schemas import (
    UserResponse,
    UserListResponse,
    ChangeStatusRequest,
    AssignRolesRequest,
    AssignLeaderRequest,
    ChangePositionRequest
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


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

    return {
        "users": users
    }


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

    return service.get_user(db, user_id)


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
# Assign roles
# ------------------------------------------------

@router.patch(
    "/{user_id}/roles",
    response_model=UserResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def assign_roles(
    user_id: UUID,
    data: AssignRolesRequest,
    db: DBSession,
    current_user: CurrentUser
):

    return service.assign_roles(db, user_id, data.role_ids)


# ------------------------------------------------
# Assign leader
# ------------------------------------------------

@router.patch(
    "/{user_id}/leader",
    response_model=UserResponse,
    dependencies=[Depends(require_roles("ADMIN", "LEADER"))]
)
def assign_leader(
    user_id: UUID,
    data: AssignLeaderRequest,
    db: DBSession,
    current_user: CurrentUser
):

    return service.assign_leader(db, user_id, data.leader_id)


# ------------------------------------------------
# Change position
# ------------------------------------------------

@router.patch(
    "/{user_id}/position",
    response_model=UserResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def change_position(
    user_id: UUID,
    data: ChangePositionRequest,
    db: DBSession,
    current_user: CurrentUser
):

    return service.change_position(db, user_id, data.position_id)