from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.organization_units import service
from app.modules.organization_units.schemas import (
    OrganizationUnitCreate,
    OrganizationUnitUpdate,
    OrganizationUnitResponse,
    OrganizationUnitListResponse
)
from app.modules.organization_units.schemas import OrganizationUnitTree

router = APIRouter(
    prefix="/organization-units",
    tags=["Organization Units"]
)


@router.get(
    "/",
    response_model=OrganizationUnitListResponse
)
def list_units(
    db: DBSession,
    current_user: CurrentUser
):

    units = service.list_units(db)

    return {
        "units": units
    }


@router.get(
    "/{unit_id}",
    response_model=OrganizationUnitResponse
)
def get_unit(
    unit_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):

    return service.get_unit(db, unit_id)


@router.post(
    "/",
    response_model=OrganizationUnitResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def create_unit(
    data: OrganizationUnitCreate,
    db: DBSession,
    current_user: CurrentUser
):

    return service.create_unit(db, data)


@router.patch(
    "/{unit_id}",
    response_model=OrganizationUnitResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def update_unit(
    unit_id: UUID,
    data: OrganizationUnitUpdate,
    db: DBSession,
    current_user: CurrentUser
):

    return service.update_unit(db, unit_id, data)


@router.delete(
    "/{unit_id}",
    response_model=OrganizationUnitResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def delete_unit(
    unit_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):

    return service.delete_unit(db, unit_id)

@router.get(
    "/tree",
    response_model=list[OrganizationUnitTree]
)
def get_units_tree(
    db: DBSession,
    current_user: CurrentUser
):

    return service.get_units_tree(db)