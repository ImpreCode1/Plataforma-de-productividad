from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
import pandas as pd

from app.models.user import User
from app.models.role import Role, UserRole


# ------------------------------------------------
# List users
# ------------------------------------------------

def list_users(db: Session):
    return db.query(User).all()


# ------------------------------------------------
# Get user with roles
# ------------------------------------------------

def get_user_with_roles(db: Session, user_id: UUID):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ------------------------------------------------
# Change status
# ------------------------------------------------

def change_status(db: Session, user_id: UUID, is_active: bool):
    user = get_user_with_roles(db, user_id)

    user.is_active = is_active
    db.commit()
    db.refresh(user)

    return user


# ------------------------------------------------
# Assign leader
# ------------------------------------------------

def assign_leader(db: Session, user_id: UUID, leader_id: UUID | None):
    user = get_user_with_roles(db, user_id)

    if leader_id:
        leader = db.query(User).filter(User.id == leader_id).first()
        if not leader:
            raise HTTPException(status_code=404, detail="Leader not found")

    user.leader_id = leader_id

    db.commit()
    db.refresh(user)

    return user


# ------------------------------------------------
# IMPORT EXCEL 🔥
# ------------------------------------------------

def import_users_from_excel(db: Session, file):

    df = pd.read_excel(file)

    created = 0
    updated = 0

    users_dict = {}

    # Primera pasada: crear usuarios
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

    # Segunda pasada: asignar líderes
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
    
def get_user_with_roles(db: Session, user_id: UUID):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔥 CLAVE
    user.roles = [ur.role for ur in user.roles]

    return user