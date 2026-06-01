import re
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from uuid import UUID
from fastapi import HTTPException
import pandas as pd


def normalize_name(name):
    if not name:
        return name
    return re.sub(r"\s+", " ", str(name).strip())


def names_match(name1, name2, threshold=0.75):
    if not name1 or not name2:
        return False

    words1 = set(normalize_name(name1).lower().split())
    words2 = set(normalize_name(name2).lower().split())

    if not words1 or not words2:
        return False

    intersection = words1 & words2
    min_words = min(len(words1), len(words2))

    return len(intersection) / min_words >= threshold


def find_user_by_fuzzy_name(users_dict, target_name):
    if not target_name:
        return None

    target = normalize_name(target_name).lower()

    for key, user in users_dict.items():
        if isinstance(key, str) and names_match(key.lower(), target):
            return user

    return None


from app.models.user import User
from app.models.role import Role, UserRole


def normalize_area(area):
    if not area:
        return None
    area = area.strip().lower()
    area_mapping = {
        "innovation business": "INNOVATION",
        "innovation": "INNOVATION",
        "human talent and administrative vice president": "HUMAN TALENT AND ADMINISTRATIVE",
        "human talent and administrative vicepresident": "HUMAN TALENT AND ADMINISTRATIVE",
        "human talent and administrative": "HUMAN TALENT AND ADMINISTRATIVE",
        "human talent": "HUMAN TALENT AND ADMINISTRATIVE",
        "human talent & administrative": "HUMAN TALENT AND ADMINISTRATIVE",
        "financial officer": "FINANCIAL OFFICER",
        "go to market": "GO TO MARKET",
        "it solutions": "IT SOLUTIONS",
        "executive office": "EXECUTIVE OFFICE",
        "expansion": "EXPANSION",
        "presidency": "PRESIDENCY",
        "human talent and administrative vp": "HUMAN TALENT AND ADMINISTRATIVE",
    }
    return area_mapping.get(area, area.upper())


def get_unique_areas(db: Session):
    areas = db.query(User.area).filter(
        User.area.isnot(None),
        User.area != "",
        User.is_active == True
    ).distinct().all()

    normalized_areas = set()
    for a in areas:
        if not a[0]:
            continue
        normalized = normalize_area(a[0].strip())
        if normalized:
            normalized_areas.add(normalized)

    return sorted(list(normalized_areas))


def list_users(db: Session):
    users = db.query(User).all()

    leader_ids = set(u.leader_id for u in users if u.leader_id)
    leaders = {}
    if leader_ids:
        leader_users = db.query(User).filter(User.id.in_(leader_ids)).all()
        leaders = {l.id: l.name for l in leader_users}

    return [
        {
            "id": u.id,
            "document_number": u.document_number,
            "name": u.name,
            "email": u.email,
            "position_name": u.position_name,
            "area": u.area,
            "subarea": u.subarea,
            "direccion": u.direccion,
            "linea": u.linea,
            "numero_linea": u.numero_linea,
            "hire_date": u.hire_date,
            "contract_type": u.contract_type,
            "salary_type": u.salary_type,
            "leader_id": u.leader_id,
            "leader_name": leaders.get(u.leader_id) if u.leader_id else None,
            "is_active": u.is_active,
            "roles": u.roles_flat,
        }
        for u in users
    ]


def get_user_with_roles(db: Session, user_id: UUID):
    user = (
        db.query(User)
        .options(
            selectinload(User.roles).selectinload(UserRole.role),
            selectinload(User.leader),
        )
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
        "direccion": user.direccion,
        "linea": user.linea,
        "numero_linea": user.numero_linea,
        "hire_date": user.hire_date,
        "contract_type": user.contract_type,
        "salary_type": user.salary_type,
        "leader_id": user.leader_id,
        "leader_name": user.leader.name if user.leader else None,
        "is_active": user.is_active,
        "roles": user.roles_flat,
    }


# ------------------------------------------------
# CREATE USER
# ------------------------------------------------


def create_user(db: Session, data):

    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_doc = (
        db.query(User).filter(User.document_number == data.document_number).first()
    )
    if existing_doc:
        raise HTTPException(
            status_code=400, detail="Document number already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        document_number=data.document_number,
        position_name=data.position_name,
        area=data.area,
        subarea=data.subarea,
        direccion=data.direccion,
        linea=data.linea,
        numero_linea=data.numero_linea,
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
        "direccion": user.direccion,
        "linea": user.linea,
        "numero_linea": user.numero_linea,
        "hire_date": user.hire_date,
        "contract_type": user.contract_type,
        "salary_type": user.salary_type,
        "leader_id": user.leader_id,
        "leader_name": user.leader.name if user.leader else None,
        "is_active": user.is_active,
        "roles": user.roles_flat,
    }


# ------------------------------------------------
# Change status
# ------------------------------------------------


def change_status(db: Session, user_id: UUID, is_active: bool):
    user = (
        db.query(User)
        .options(selectinload(User.leader))
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = is_active

    if not is_active:
        user.leader_id = None

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
        "direccion": user.direccion,
        "linea": user.linea,
        "numero_linea": user.numero_linea,
        "hire_date": user.hire_date,
        "contract_type": user.contract_type,
        "salary_type": user.salary_type,
        "leader_id": user.leader_id,
        "leader_name": user.leader.name if user.leader else None,
        "is_active": user.is_active,
        "roles": user.roles_flat,
    }


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
        "roles": user.roles_flat,
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

    if "name" in data and data["name"]:
        user.name = data["name"]
    if "email" in data and data["email"]:
        user.email = data["email"]
    if "document_number" in data and data["document_number"]:
        user.document_number = data["document_number"]

    new_position = data.get("position_name")
    new_area = data.get("area")
    new_subarea = data.get("subarea")
    new_direccion = data.get("direccion")
    new_linea = data.get("linea")
    new_numero_linea = data.get("numero_linea")

    if new_position is not None:
        user.position_name = new_position
    if new_area is not None:
        user.area = new_area
    if new_subarea is not None:
        user.subarea = new_subarea
    if new_direccion is not None:
        user.direccion = new_direccion
    if new_linea is not None:
        user.linea = new_linea
    if new_numero_linea is not None:
        user.numero_linea = new_numero_linea

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
        "roles": user.roles_flat,
    }


# ------------------------------------------------
# IMPORT EXCEL
# ------------------------------------------------


def import_users_from_excel(db: Session, file):

    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()

    created = 0
    updated = 0

    users_dict = {}

    column_mapping = {
        "C.C. No.": "document_number",
        "NOMBRE COLABORADOR": "name",
        "CORREO": "email",
        "CARGO": "position_name",
        "AREA": "area",
        "SUBAREA/DIVISION": "subarea",
        "FECHA DE INGRESO": "hire_date",
        "TIPO DE CONTRATO": "contract_type",
        "TIPO DE SALARIO": "salary_type",
    }

    for _, row in df.iterrows():
        email = row["CORREO"]
        if pd.isna(email) or not email:
            continue

        user = db.query(User).filter(User.email == email).first()

        hire_date = None
        if "FECHA DE INGRESO" in row and not pd.isna(row.get("FECHA DE INGRESO")):
            hire_date = row["FECHA DE INGRESO"]
            if isinstance(hire_date, str):
                try:
                    hire_date = datetime.strptime(hire_date, "%Y-%m-%d").date()
                except:
                    try:
                        hire_date = datetime.strptime(hire_date, "%d/%m/%Y").date()
                    except:
                        hire_date = None

        if not user:
            user = User(
                document_number=str(row["C.C. No."]),
                name=row["NOMBRE COLABORADOR"],
                email=email,
                position_name=row.get("CARGO")
                if not pd.isna(row.get("CARGO"))
                else None,
                area=row.get("AREA") if not pd.isna(row.get("AREA")) else None,
                subarea=row.get("SUBAREA/DIVISION")
                if not pd.isna(row.get("SUBAREA/DIVISION"))
                else None,
                hire_date=hire_date,
                contract_type=row.get("TIPO DE CONTRATO")
                if not pd.isna(row.get("TIPO DE CONTRATO"))
                else None,
                salary_type=row.get("TIPO DE SALARIO")
                if not pd.isna(row.get("TIPO DE SALARIO"))
                else None,
            )
            db.add(user)
            created += 1
        else:
            user.name = row["NOMBRE COLABORADOR"]
            user.position_name = (
                row.get("CARGO")
                if not pd.isna(row.get("CARGO"))
                else user.position_name
            )
            user.area = row.get("AREA") if not pd.isna(row.get("AREA")) else user.area
            user.subarea = (
                row.get("SUBAREA/DIVISION")
                if not pd.isna(row.get("SUBAREA/DIVISION"))
                else user.subarea
            )
            user.hire_date = hire_date if hire_date else user.hire_date
            user.contract_type = (
                row.get("TIPO DE CONTRATO")
                if not pd.isna(row.get("TIPO DE CONTRATO"))
                else user.contract_type
            )
            user.salary_type = (
                row.get("TIPO DE SALARIO")
                if not pd.isna(row.get("TIPO DE SALARIO"))
                else user.salary_type
            )
            updated += 1

        users_dict[normalize_name(user.name).lower()] = user
        users_dict[user.email.strip().lower()] = user
        users_dict[user.name] = user

    db.commit()

    for _, row in df.iterrows():
        user_name = normalize_name(row["NOMBRE COLABORADOR"])
        user = users_dict.get(user_name) or users_dict.get(user_name.lower())
        if not user:
            continue

        leader_name = row.get("JEFE DIRECTO")
        leader_cell = str(leader_name).strip() if leader_name is not None else ""

        if (
            leader_cell == ""
            or str(leader_name).lower() in ["nan", "none", "null", "nil"]
            or str(leader_name) == ""
        ):
            user.leader_id = None
            continue

        leader_name = normalize_name(leader_name)
        if leader_name:
            leader = users_dict.get(leader_name) or users_dict.get(leader_name.lower())
            if not leader:
                leader = find_user_by_fuzzy_name(users_dict, leader_name)
            if not leader:
                leader = (
                    db.query(User).filter(User.name.ilike(f"%{leader_name}%")).first()
                )

            if leader:
                user.leader_id = leader.id

    db.commit()

    leader_role = db.query(Role).filter(Role.name == "LEADER").first()
    employee_role = db.query(Role).filter(Role.name == "EMPLOYEE").first()

    if not leader_role or not employee_role:
        raise HTTPException(status_code=500, detail="Roles LEADER or EMPLOYEE not found in database")

    subordinate_ids = set()
    for user in users_dict.values():
        if user.leader_id:
            subordinate_ids.add(user.leader_id)

    unique_users = set(users_dict.values())

    for user in unique_users:
        db.query(UserRole).filter(UserRole.user_id == user.id).delete(synchronize_session=False)

        if user.id in subordinate_ids:
            db.add(UserRole(user_id=user.id, role_id=leader_role.id))
        else:
            db.add(UserRole(user_id=user.id, role_id=employee_role.id))

    db.commit()

    return {"created": created, "updated": updated}
