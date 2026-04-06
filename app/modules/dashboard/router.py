from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.dashboard import service
from app.modules.dashboard.schemas import DashboardResponse, TeamDashboardResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


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