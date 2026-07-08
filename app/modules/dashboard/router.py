from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.models.user import User
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
    db: DBSession,
    current_user: CurrentUser,
    year: int = Query(default=...),
    month: Optional[int] = Query(default=None),
):
    return service.get_team_dashboard(db, current_user.id, year, month)


# ------------------------------------------------
# GLOBAL DASHBOARD (ADMIN)
# ------------------------------------------------

@router.get(
    "/global",
    response_model=dict
)
def get_global_dashboard(
    year: int = Query(default=...),
    month: Optional[int] = Query(default=None),
    quarter: Optional[int] = Query(default=None, ge=1, le=4),
    area: Optional[str] = Query(default=None),
    direccion: Optional[str] = Query(default=None),
    subarea: Optional[str] = Query(default=None),
    responsable: Optional[str] = Query(default=None),
    cumplimiento: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    return service.get_global_dashboard(
        db, year, month, quarter, area, direccion, subarea,
        responsable, cumplimiento, search
    )


# ------------------------------------------------
# FILTER OPTIONS
# ------------------------------------------------

@router.get(
    "/filters/subareas",
    response_model=list[str]
)
def get_subareas(
    area: Optional[str] = Query(default=None),
    direccion: Optional[str] = Query(default=None),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    from app.modules.users.service import get_unique_subareas
    return get_unique_subareas(db, area=area, direccion=direccion)


@router.get(
    "/filters/direcciones",
    response_model=list[str]
)
def get_direcciones(
    area: Optional[str] = Query(default=None),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    from app.modules.users.service import get_unique_direcciones
    return get_unique_direcciones(db, area=area)


@router.get(
    "/filters/responsables",
    response_model=list[str]
)
def get_responsables(
    area: Optional[str] = Query(default=None),
    direccion: Optional[str] = Query(default=None),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    from app.modules.users.service import get_unique_responsables
    return get_unique_responsables(db, area=area, direccion=direccion)


# ------------------------------------------------
# GLOBAL REPORT EXCEL (ADMIN)
# ------------------------------------------------

@router.get(
    "/global/report",
    dependencies=[Depends(require_roles("ADMIN"))]
)
def get_global_report(
    year: int = Query(default=...),
    area: Optional[str] = Query(default=None),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    excel_file = service.generate_global_report(db, year, area)
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=reporte_kpi_{year}.xlsx"}
    )