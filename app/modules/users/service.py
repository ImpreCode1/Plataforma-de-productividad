from typing import cast
from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role, UserRole
from app.modules.users.schemas import UserResponse


# ------------------------------------------------
# List users
# ------------------------------------------------

def list_users(db: Session):

    users = db.query(User).options(
        selectinload(User.user_roles).selectinload(UserRole.role),
        selectinload(User.position),
        selectinload(User.leader)
    ).all()

    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            position_id=user.position_id,
            leader_id=user.leader_id,
            roles=[ur.role.name for ur in user.user_roles],  # 🔥 FIX
            position=user.position,
            leader_name=user.leader.name if user.leader else None
        )
        for user in users
    ]


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


def get_user_with_roles(db: Session, user_id: UUID):

    user = db.query(User).options(
        selectinload(User.user_roles).selectinload(UserRole.role),
        selectinload(User.position),
        selectinload(User.leader)
    ).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        position_id=user.position_id,
        leader_id=user.leader_id,
        roles=[ur.role.name for ur in user.user_roles],  # 🔥 AQUÍ ESTÁ LA CLAVE
        position=user.position,
        leader_name=user.leader.name if user.leader else None
    )

# ------------------------------------------------
# Change status
# ------------------------------------------------

def change_status(db: Session, user_id: UUID, is_active: bool):

    user = get_user(db, user_id)

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    user = db.query(User).options(
        selectinload(User.user_roles).selectinload(UserRole.role),
        selectinload(User.position),
        selectinload(User.leader)
    ).filter(User.id == user_id).first()

    return user


# ------------------------------------------------
# Assign roles
# ------------------------------------------------

def assign_roles(db: Session, user_id: UUID, role_ids: list[UUID]):

    user = get_user(db, user_id)

    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    
    for role_id in role_ids:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
    
    db.commit()
    
    user = db.query(User).options(
        selectinload(User.user_roles).selectinload(UserRole.role),
        selectinload(User.position),
        selectinload(User.leader)
    ).filter(User.id == user_id).first()

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

    user = db.query(User).options(
        selectinload(User.user_roles).selectinload(UserRole.role),
        selectinload(User.position),
        selectinload(User.leader)
    ).filter(User.id == user_id).first()

    return user


# ------------------------------------------------
# Change position
# ------------------------------------------------

def change_position(db: Session, user_id: UUID, position_id: UUID | None):

    user = get_user(db, user_id)

    user.position_id = position_id

    db.commit()
    db.refresh(user)

    user = db.query(User).options(
        selectinload(User.user_roles).selectinload(UserRole.role),
        selectinload(User.position),
        selectinload(User.leader)
    ).filter(User.id == user_id).first()

    return user