from sqlalchemy.orm import Session
from uuid import UUID
from app.models import Role


class RoleService:

    @staticmethod
    def list_roles(db: Session):

        return db.query(Role).all()

    @staticmethod
    def create_role(db: Session, data):

        role = Role(
            name=data.name,
            description=data.description
        )

        db.add(role)
        db.commit()
        db.refresh(role)

        return role

    @staticmethod
    def get_role(db: Session, role_id: UUID):

        return db.query(Role).filter(
            Role.id == role_id
        ).first()

    @staticmethod
    def update_role(db: Session, role_id: UUID, data):

        role = db.query(Role).filter(
            Role.id == role_id
        ).first()

        if role:
            role.name = data.name
            role.description = data.description

            db.commit()
            db.refresh(role)

        return role

    @staticmethod
    def delete_role(db: Session, role_id: UUID):

        role = db.query(Role).filter(
            Role.id == role_id
        ).first()

        if role:
            db.delete(role)
            db.commit()

        return role