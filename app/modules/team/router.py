from fastapi import APIRouter, Depends

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.team import service
from app.modules.team.schemas import TeamMembersResponse

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
