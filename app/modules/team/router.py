from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.team import service
from app.modules.team.schemas import TeamMembersResponse, AllTeamsResponse

router = APIRouter(
    prefix="/team",
    tags=["Team"]
)


@router.get(
    "/members",
    response_model=TeamMembersResponse,
    dependencies=[Depends(require_roles("LEADER", "ADMIN"))]
)
def get_team_members(
    db: DBSession,
    current_user: CurrentUser
):
    members = service.get_team_members(db, current_user.id)
    return {"members": members}


@router.get(
    "/all",
    response_model=AllTeamsResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def get_all_teams(
    db: DBSession,
    current_user: CurrentUser
):
    teams = service.get_all_teams(db)
    return {"teams": teams}


@router.get(
    "/{user_id}/members",
    response_model=TeamMembersResponse,
    dependencies=[Depends(require_roles("ADMIN"))]
)
def get_team_members_by_user(
    user_id: UUID,
    db: DBSession,
    current_user: CurrentUser
):
    members = service.get_team_members(db, user_id)
    return {"members": members}
