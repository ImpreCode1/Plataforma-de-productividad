from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.special_mode import service
from app.modules.special_mode.schemas import (
    ApprovalConfigCreate,
    ApprovalConfigUpdate,
    ApprovalConfigResponse,
    ApprovalConfigListResponse,
    LoadModeCheck,
)

router = APIRouter(
    prefix="/approval-config",
    tags=["Approval Config"],
)


@router.post(
    "/",
    response_model=ApprovalConfigResponse,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def create_config(
    data: ApprovalConfigCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    return service.create_config(db, data.config_type, data.config_value, data.load_mode, current_user.id)


@router.get(
    "/",
    response_model=ApprovalConfigListResponse,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def list_configs(
    config_type: Optional[str] = Query(None),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser,
):
    configs = service.list_configs(db, config_type)
    return {"configs": configs}


@router.get(
    "/check/{user_id}",
    response_model=LoadModeCheck,
)
def check_load_mode(
    user_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    mode = service.get_load_mode(db, user_id)
    return {"user_id": user_id, "load_mode": mode}


@router.patch(
    "/{config_id}",
    response_model=ApprovalConfigResponse,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def update_config(
    config_id: UUID,
    data: ApprovalConfigUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    return service.update_config(db, config_id, data.load_mode)


@router.delete(
    "/{config_id}",
    dependencies=[Depends(require_roles("ADMIN"))],
)
def delete_config(
    config_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    service.delete_config(db, config_id)
    return {"message": "Configuración eliminada"}
