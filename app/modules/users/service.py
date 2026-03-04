from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.position import Position
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.modules.users.schemas import UserCreate, UserUpdate

def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user

def create_user(db: Session, payload: UserCreate) -> User:
    user = User(**payload.model_dump())

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo o external_auth_id ya existe",
        )

    db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: UUID):
    user = get_user_by_id(db, user_id)
    user.is_active = False
    db.commit()

def list_users(db: Session):
    return db.scalars(select(User)).all()

def get_user(db: Session, user_id: UUID):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

def change_status(db: Session, user_id: UUID, is_active: bool):
    user = get_user(db, user_id)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def assign_roles(db: Session, user_id: UUID, role_ids: list[UUID]):
    user = get_user(db, user_id)

    # Validar que los roles existan
    roles = db.scalars(select(Role).where(Role.id.in_(role_ids))).all()

    if len(roles) != len(role_ids):
        raise HTTPException(status_code=400, detail="Algún rol no existe")

    # Borrar roles actuales
    db.execute(delete(UserRole).where(UserRole.user_id == user_id))

    # Crear nuevos
    for role in roles:
        db.add(UserRole(user_id=user_id, role_id=role.id))

    db.commit()
    db.refresh(user)
    return user


def assign_leader(db: Session, user_id: UUID, leader_id: UUID | None):
    user = get_user(db, user_id)

    if leader_id == user_id:
        raise HTTPException(status_code=400, detail="No puede ser su propio líder")

    if leader_id:
        leader = db.get(User, leader_id)
        if not leader:
            raise HTTPException(status_code=400, detail="Líder no existe")

    user.leader_id = leader_id
    db.commit()
    db.refresh(user)
    return user


def change_position(db: Session, user_id: UUID, position_id: UUID | None):
    user = get_user(db, user_id)

    if position_id:
        position = db.get(Position, position_id)
        if not position:
            raise HTTPException(status_code=400, detail="Posición no existe")

    user.position_id = position_id
    db.commit()
    db.refresh(user)
    return user