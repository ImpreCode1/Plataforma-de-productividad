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
# CREATE USER
# ------------------------------------------------

def create_user(db: Session, data):
    # Validaremail único
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validar documento único
    existing_doc = db.query(User).filter(User.document_number == data.document_number).first()
    if existing_doc:
        raise HTTPException(status_code=400, detail="Document number already registered")

    user = User(
        name=data.name,
        email=data.email,
        document_number=data.document_number,
        position_name=data.position_name,
        area=data.area,
        subarea=data.subarea,
    )

    db.add(user)
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
        "roles": []
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
# Update user
# ------------------------------------------------

def update_user(db: Session, user_id: UUID, data: dict):
    from datetime import datetime
    from app.models.indicator_assignment import IndicatorAssignment
    from app.models.tracking import IndicatorTracking

    user = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_position = user.position_name
    old_area = user.area
    old_subarea = user.subarea

    if "name" in data and data["name"]:
        user.name = data["name"]
    if "email" in data and data["email"]:
        user.email = data["email"]
    if "document_number" in data and data["document_number"]:
        user.document_number = data["document_number"]

    new_position = data.get("position_name")
    new_area = data.get("area")
    new_subarea = data.get("subarea")

    if new_position is not None:
        user.position_name = new_position
    if new_area is not None:
        user.area = new_area
    if new_subarea is not None:
        user.subarea = new_subarea

    position_changed = "position_name" in data
    area_changed = "area" in data
    subarea_changed = "subarea" in data

    if position_changed or area_changed:
        current_month = datetime.now().month
        current_year = datetime.now().year

        active_assignments = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.user_id == user_id,
            IndicatorAssignment.year == current_year,
            IndicatorAssignment.is_active == True
        ).all()

        from_month = current_month + 1

        for assignment in active_assignments:
            if assignment.end_month >= current_month:
                assignment.end_month = current_month - 1
                if assignment.end_month < assignment.start_month:
                    assignment.end_month = assignment.start_month
                    assignment.is_active = False

                trackings_futuros = db.query(IndicatorTracking).filter(
                    IndicatorTracking.assignment_id == assignment.id,
                    IndicatorTracking.month >= from_month
                ).all()

                for tracking in trackings_futuros:
                    from app.models.evidence import Evidence
                    db.query(Evidence).filter(
                        Evidence.tracking_id == tracking.id
                    ).update({
                        Evidence.tracking_id: None,
                        Evidence.user_id: user_id,
                        Evidence.year: tracking.year,
                        Evidence.month: tracking.month
                    })
                    db.delete(tracking)

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