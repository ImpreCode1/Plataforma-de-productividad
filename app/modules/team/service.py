from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User


def get_team_members(db: Session, leader_id: UUID) -> list[User]:
    return db.query(User).filter(
        User.leader_id == leader_id,
        User.is_active == True
    ).all()
