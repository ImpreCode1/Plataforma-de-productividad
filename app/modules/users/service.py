from typing import cast
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role


# ------------------------------------------------
# List users
# ------------------------------------------------

def list_users(db: Session):

    users = db.query(User).all()

    return users


# ------------------------------------------------
# Get user
# ------------------------------------------------

def get_user(db: Session, user_id: UUID):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return user


# ------------------------------------------------
# Change status
# ------------------------------------------------

def change_status(db: Session, user_id: UUID, is_active: bool):

    user = get_user(db, user_id)

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user


# ------------------------------------------------
# Assign roles
# ------------------------------------------------

def assign_roles(db: Session, user_id: UUID, role_ids: list[UUID]):

    user = get_user(db, user_id)

    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    user.roles = roles

    db.commit()
    db.refresh(user)

    return user


# ------------------------------------------------
# Assign leader
# ------------------------------------------------

def assign_leader(db: Session, user_id: UUID, leader_id: UUID | None):

    user = get_user(db, user_id)

    if leader_id:

        leader = db.query(User).filter(User.id == leader_id).first()

        if not leader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Líder no encontrado",
            )

    user.leader_id = leader_id

    db.commit()
    db.refresh(user)

    return user


# ------------------------------------------------
# Change position
# ------------------------------------------------

def change_position(db: Session, user_id: UUID, position_id: UUID | None):

    user = get_user(db, user_id)

    user.position_id = position_id

    db.commit()
    db.refresh(user)

    return user