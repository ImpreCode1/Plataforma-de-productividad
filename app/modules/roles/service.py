from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.role import Role, UserRole
from app.models.user import User


class RoleService:

    # ------------------------------------------------
    # LIST
    # ------------------------------------------------

    @staticmethod
    def list_roles(db: Session):
        return db.query(Role).all()

    # ------------------------------------------------
    # CREATE
    # ------------------------------------------------

    @staticmethod
    def create_role(db: Session, data):

        existing = db.query(Role).filter(
            Role.name == data.name
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Role already exists")

        role = Role(name=data.name)

        db.add(role)
        db.commit()
        db.refresh(role)

        return role

    # ------------------------------------------------
    # GET
    # ------------------------------------------------

    @staticmethod
    def get_role(db: Session, role_id: UUID):

        role = db.query(Role).filter(
            Role.id == role_id
        ).first()

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        return role

    # ------------------------------------------------
    # UPDATE
    # ------------------------------------------------

    @staticmethod
    def update_role(db: Session, role_id: UUID, data):

        role = db.query(Role).filter(
            Role.id == role_id
        ).first()

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        role.name = data.name

        db.commit()
        db.refresh(role)

        return role

    # ------------------------------------------------
    # DELETE
    # ------------------------------------------------

    @staticmethod
    def delete_role(db: Session, role_id: UUID):

        role = db.query(Role).filter(
            Role.id == role_id
        ).first()

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        db.delete(role)
        db.commit()

        return {"message": "Role deleted"}

    # ------------------------------------------------
    # 🔥 ASSIGN ROLES (CRÍTICO)
    # ------------------------------------------------

    @staticmethod
    def assign_roles(db: Session, user_id: UUID, role_ids: list[UUID]):

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # validar roles
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

        if len(roles) != len(role_ids):
            raise HTTPException(status_code=400, detail="Some roles do not exist")

        # eliminar actuales
        db.query(UserRole).filter(
            UserRole.user_id == user_id
        ).delete()

        # asignar nuevos
        for role_id in role_ids:
            db.add(UserRole(
                user_id=user_id,
                role_id=role_id
            ))

        db.commit()

        # devolver usuario actualizado
        db.refresh(user)

        return user