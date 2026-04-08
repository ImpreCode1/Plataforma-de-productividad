from uuid import UUID
from fastapi import APIRouter, Depends, Query

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.dashboard import service
from app.modules.dashboard.schemas import DashboardResponse, TeamDashboardResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ------------------------------------------------
# MY DASHBOARD
# ------------------------------------------------

@router.get(
    "/me",
    response_model=DashboardResponse
)
def get_my_dashboard(
    year: int = Query(default=..., description="Año del dashboard"),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    return service.get_dashboard_by_user(db, current_user.id, year)


# ------------------------------------------------
# USER DASHBOARD
# ------------------------------------------------

@router.get(
    "/user/{user_id}",
    response_model=DashboardResponse
)
def get_user_dashboard(
    user_id: UUID,
    year: int,
    db: DBSession,
    current_user: CurrentUser
):
    return service.get_dashboard_by_user(db, user_id, year)


# ------------------------------------------------
# TEAM DASHBOARD (LEADER)
# ------------------------------------------------

@router.get(
    "/team",
    response_model=TeamDashboardResponse,
    dependencies=[Depends(require_roles("LEADER", "ADMIN"))]
)
def get_team_dashboard(
    year: int,
    db: DBSession,
    current_user: CurrentUser
):
    return service.get_team_dashboard(db, current_user.id, year)