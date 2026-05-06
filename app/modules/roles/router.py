from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.roles.service import RoleService
from app.modules.roles.schemas import (
    RoleResponse,
    RoleListResponse,
    CreateRoleRequest,
    UpdateRoleRequest,
    AssignRolesRequest
)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


# ------------------------------------------------
# LIST ROLES
# ------------------------------------------------

@router.get(
    "/",
    response_model=RoleListResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def list_roles(
    db: DBSession,
    current_user: CurrentUser
):
    roles = RoleService.list_roles(db)
    return {"roles": roles}


# ------------------------------------------------
# CREATE ROLE (opcional)
# ------------------------------------------------

@router.post(
    "/",
    response_model=RoleResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def create_role(
    data: CreateRoleRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return RoleService.create_role(db, data)


# ------------------------------------------------
# UPDATE ROLE
# ------------------------------------------------

@router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def update_role(
    role_id: UUID,
    data: UpdateRoleRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return RoleService.update_role(db, role_id, data)


# ------------------------------------------------
# DELETE ROLE
# ------------------------------------------------

@router.delete(
    "/{role_id}",
    dependencies=[Depends(require_roles("ADMIN"))]
)
def delete_role(
    role_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    return RoleService.delete_role(db, role_id)


# ------------------------------------------------
# 🔥 ASSIGN ROLES A USER
# ------------------------------------------------

@router.patch(
    "/users/{user_id}",
    dependencies=[Depends(require_roles("ADMIN"))]
)
def assign_roles(
    user_id: UUID,
    data: AssignRolesRequest,
    db: DBSession,
    current_user: CurrentUser
):
    return RoleService.assign_roles(db, user_id, data.role_ids)