from sqlalchemy.orm import Session, selectinload
from uuid import UUID
from fastapi import HTTPException
import pandas as pd

from app.models.user import User
from app.models.role import Role, UserRole


def list_users(db: Session):
    users = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .all()
    )
    
    return [
        {
            "id": u.id,
            "document_number": u.document_number,
            "name": u.name,
            "email": u.email,
            "position_name": u.position_name,
            "area": u.area,
            "subarea": u.subarea,
            "hire_date": u.hire_date,
            "contract_type": u.contract_type,
            "salary_type": u.salary_type,
            "leader_id": u.leader_id,
            "is_active": u.is_active,
            "roles": u.roles_flat
        }
        for u in users
    ]


def get_user_with_roles(db: Session, user_id: UUID):
    user = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "document_number": user.document_number,
        "name": user.name,
        "email": user.email,
        "position_name": user.position_name,
        "area": user.area,
        "subarea": user.subarea,
        "hire_date": user.hire_date,
        "contract_type": user.contract_type,
        "salary_type": user.salary_type,
        "leader_id": user.leader_id,
        "is_active": user.is_active,
        "roles": user.roles_flat
    }


# ------------------------------------------------
# Change status
# ------------------------------------------------

def change_status(db: Session, user_id: UUID, is_active: bool):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = is_active
    db.commit()
    db.refresh(user)

    return {"message": "Status updated"}


# ------------------------------------------------
# Assign leader
# ------------------------------------------------

def assign_leader(db: Session, user_id: UUID, leader_id: UUID | None):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if leader_id:
        leader = db.query(User).filter(User.id == leader_id).first()
        if not leader:
            raise HTTPException(status_code=404, detail="Leader not found")

    user.leader_id = leader_id

    db.commit()
    db.refresh(user)

    return {"message": "Leader assigned"}


# ------------------------------------------------
# Update user
# ------------------------------------------------

def update_user(db: Session, user_id: UUID, data: dict):
    user = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "name" in data and data["name"]:
        user.name = data["name"]
    if "email" in data and data["email"]:
        user.email = data["email"]
    if "document_number" in data and data["document_number"]:
        user.document_number = data["document_number"]
    if "position_name" in data:
        user.position_name = data["position_name"]
    if "area" in data:
        user.area = data["area"]
    if "subarea" in data:
        user.subarea = data["subarea"]

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "document_number": user.document_number,
        "name": user.name,
        "email": user.email,
        "position_name": user.position_name,
        "area": user.area,
        "subarea": user.subarea,
        "hire_date": user.hire_date,
        "contract_type": user.contract_type,
        "salary_type": user.salary_type,
        "leader_id": user.leader_id,
        "is_active": user.is_active,
        "roles": user.roles_flat
    }


# ------------------------------------------------
# IMPORT EXCEL 🔥 (bien hecho)
# ------------------------------------------------

def import_users_from_excel(db: Session, file):

    df = pd.read_excel(file)

    created = 0
    updated = 0

    users_dict = {}

    # Primera pasada: crear/actualizar usuarios
    for _, row in df.iterrows():

        email = row["EMAIL"]

        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(
                document_number=str(row["C.C. No."]),
                name=row["NOMBRE COLABORADOR"],
                email=email,
                position_name=row.get("CARGO"),
                area=row.get("AREA (VP)"),
                subarea=row.get("SUBAREA (División)"),
            )
            db.add(user)
            created += 1
        else:
            user.name = row["NOMBRE COLABORADOR"]
            user.position_name = row.get("CARGO")
            user.area = row.get("AREA (VP)")
            user.subarea = row.get("SUBAREA (División)")
            updated += 1

        users_dict[user.name] = user

    db.commit()

    # Segunda pasada: líderes
    for _, row in df.iterrows():
        user = users_dict.get(row["NOMBRE COLABORADOR"])
        leader_name = row.get("JEFE DIRECTO")

        if leader_name and leader_name in users_dict:
            user.leader_id = users_dict[leader_name].id

    db.commit()

    return {
        "created": created,
        "updated": updated
    }