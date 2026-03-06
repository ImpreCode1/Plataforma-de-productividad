from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.positions import service
from app.modules.positions.schemas import (
    PositionCreate,
    PositionUpdate,
    PositionResponse,
    PositionListResponse,
)

router = APIRouter(prefix="/positions", tags=["Positions"])


# -----------------------------------------
# List positions
# -----------------------------------------


@router.get("/", response_model=PositionListResponse)
def list_positions(db: DBSession, current_user: CurrentUser):

    positions = service.get_positions(db)

    return {"positions": positions}


# -----------------------------------------
# Get position
# -----------------------------------------


@router.get("/{position_id}", response_model=PositionResponse)
def get_position(position_id: UUID, db: DBSession, current_user: CurrentUser):

    return service.get_position(db, position_id)


# -----------------------------------------
# Create position
# -----------------------------------------


@router.post(
    "/", response_model=PositionResponse, dependencies=[Depends(require_roles("ADMIN"))]
)
def create_position(data: PositionCreate, db: DBSession, current_user: CurrentUser):

    return service.create_position(db, data)


# -----------------------------------------
# Update position
# -----------------------------------------


@router.patch(
    "/{position_id}",
    response_model=PositionResponse,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def update_position(
    position_id: UUID, data: PositionUpdate, db: DBSession, current_user: CurrentUser
):

    return service.update_position(db, position_id, data)


# -----------------------------------------
# Delete position
# -----------------------------------------


@router.delete(
    "/{position_id}",
    response_model=PositionResponse,
    dependencies=[Depends(require_roles("ADMIN"))],
)
def delete_position(position_id: UUID, db: DBSession, current_user: CurrentUser):

    return service.delete_position(db, position_id)
