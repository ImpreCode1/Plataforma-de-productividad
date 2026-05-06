from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from app.models.user import User


def get_team_members(db: Session, leader_id: UUID) -> list[User]:
    return (
        db.query(User).filter(User.leader_id == leader_id, User.is_active == True).all()
    )


def get_all_teams(db: Session):
    leaders = (
        db.query(User)
        .filter(
            User.id.in_(
                db.query(User.leader_id).distinct().where(User.leader_id.isnot(None))
            )
        )
        .options(selectinload(User.subordinates))
        .all()
    )

    teams = []
    for leader in leaders:
        members = leader.subordinates or []
        active_members = [m for m in members if m.is_active]

        teams.append(
            {
                "leader": {
                    "id": leader.id,
                    "name": leader.name,
                    "email": leader.email,
                    "position_name": leader.position_name,
                    "area": leader.area,
                },
                "members": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "email": m.email,
                        "position_name": m.position_name,
                        "area": m.area,
                    }
                    for m in active_members
                ],
                "count": len(active_members),
            }
        )

    users_without_leader = (
        db.query(User).filter(User.leader_id == None, User.is_active == True).all()
    )

    teams.append(
        {
            "leader": None,
            "members": [
                {
                    "id": m.id,
                    "name": m.name,
                    "email": m.email,
                    "position_name": m.position_name,
                    "area": m.area,
                }
                for m in users_without_leader
            ],
            "count": len(users_without_leader),
            "is_unassigned": True,
        }
    )

    return teams
