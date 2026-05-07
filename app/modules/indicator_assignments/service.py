import logging

from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)

from app.models.indicator_assignment import IndicatorAssignment
from app.models.tracking import IndicatorTracking
from app.models.user import User


def normalize_name(name):
    if not name:
        return name
    return re.sub(r"\s+", " ", str(name).strip())


def names_match(name1, name2, threshold=0.6):
    if not name1 or not name2:
        return False
    words1 = set(normalize_name(name1).lower().split())
    words2 = set(normalize_name(name2).lower().split())
    if not words1 or not words2:
        return False
    intersection = words1 & words2
    min_words = min(len(words1), len(words2))
    if min_words == 0:
        return False
    return len(intersection) / min_words >= threshold


def find_user_by_fuzzy_name(users_dict, target_name):
    if not target_name:
        return None
    target = normalize_name(target_name).lower()
    for key, user in users_dict.items():
        if isinstance(key, str) and names_match(key.lower(), target):
            return user
    return None


# ------------------------------------------------
# CREATE
# ------------------------------------------------

def create_assignment(db: Session, data):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.user_id == data.user_id,
        IndicatorAssignment.year == data.year,
        IndicatorAssignment.month == data.month,
        IndicatorAssignment.indicator_name == data.indicator_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Indicator already exists for this user/year/month")

    assignment = IndicatorAssignment(
        user_id=data.user_id,
        indicator_name=data.indicator_name,
        formula=data.formula,
        year=data.year,
        month=data.month,
        target_value=data.target_value,
        weight=data.weight,
        frequency=data.frequency,
        position_name_at_assignment=user.position_name,
        area_at_assignment=user.area,
        subarea_at_assignment=user.subarea,
        direccion_at_assignment=user.direccion,
        linea_at_assignment=user.linea,
        numero_linea_at_assignment=user.numero_linea
    )

    db.add(assignment)
    db.commit()

    db.commit()
    db.refresh(assignment)

    return assignment


# ------------------------------------------------
# LIST
# ------------------------------------------------

def list_assignments(db: Session, user_id: UUID, year: int, month: int = None):
    query = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.user_id == user_id,
        IndicatorAssignment.year == year
    )
    if month:
        query = query.filter(IndicatorAssignment.month == month)
    return query.all()


# ------------------------------------------------
# LIST ALL
# ------------------------------------------------

def list_all_assignments(db: Session, year: int | None = None, month: int | None = None):
    query = db.query(IndicatorAssignment)
    if year:
        query = query.filter(IndicatorAssignment.year == year)
    if month:
        query = query.filter(IndicatorAssignment.month == month)
    return query.all()


# ------------------------------------------------
# UPDATE
# ------------------------------------------------

def update_assignment(db: Session, assignment_id: UUID, data):
    assignment = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(assignment, field, value)

    db.commit()
    db.refresh(assignment)

    return assignment


# ------------------------------------------------
# DELETE
# ------------------------------------------------

def delete_assignment(db: Session, assignment_id: UUID):
    assignment = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    trackings = db.query(IndicatorTracking).filter(
        IndicatorTracking.assignment_id == assignment_id
    ).all()
    
    tracking_ids = [t.id for t in trackings]

    if tracking_ids:
        from app.models.evidence import Evidence
        from app.models.action_plan import ActionPlan
        
        db.query(Evidence).filter(Evidence.tracking_id.in_(tracking_ids)).delete(synchronize_session=False)
        db.query(ActionPlan).filter(ActionPlan.tracking_id.in_(tracking_ids)).delete(synchronize_session=False)

    db.query(IndicatorTracking).filter(
        IndicatorTracking.assignment_id == assignment_id
    ).delete()

    db.delete(assignment)
    db.commit()


# ------------------------------------------------
# CLOSE ASSIGNMENT
# ------------------------------------------------

def close_assignment(db: Session, assignment_id: UUID):
    assignment = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.is_active = False

    db.commit()
    db.refresh(assignment)
    return assignment


# ------------------------------------------------
# REOPEN ASSIGNMENT (create new with updated position)
# ------------------------------------------------

def reopen_assignment(db: Session, assignment_id: UUID, month: int, new_indicators: dict):
    original = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.id == assignment_id
    ).first()

    if not original:
        raise HTTPException(status_code=404, detail="Assignment not found")

    user = db.query(User).filter(User.id == original.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    created_assignments = []

    for indicator_name, values in new_indicators.items():
        existing = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.user_id == original.user_id,
            IndicatorAssignment.year == original.year,
            IndicatorAssignment.month == month,
            IndicatorAssignment.indicator_name == indicator_name
        ).first()

        if existing:
            continue

        assignment = IndicatorAssignment(
            user_id=original.user_id,
            indicator_name=indicator_name,
            formula=values.get("formula"),
            year=original.year,
            month=month,
            target_value=values["target_value"],
            weight=values["weight"],
            frequency=values.get("frequency", "MONTHLY"),
            position_name_at_assignment=user.position_name,
            area_at_assignment=user.area,
            subarea_at_assignment=user.subarea
        )
        db.add(assignment)
        created_assignments.append((assignment, month))

    db.commit()
    return created_assignments


# ------------------------------------------------
# IMPORT EXCEL 🔥
# ------------------------------------------------

MONTHS_MAP = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

def safe_float(value, default=0):
    if value is None or pd.isna(value):
        return default
    try:
        return float(value)
    except:
        return default


def import_assignments_from_excel(db: Session, file, year: int, month: int = None):
    df = pd.read_excel(file)

    created = 0
    updated = 0

    users_by_name = {}
    all_users = db.query(User).all()
    for user in all_users:
        users_by_name[user.name.lower().strip()] = user

    for _, row in df.iterrows():
        responsible_name = str(row["Responsable"]).lower().strip()
        user = users_by_name.get(responsible_name)
        
        if not user:
            user = find_user_by_fuzzy_name(users_by_name, responsible_name)
        
        if not user:
            logger.warning(f"Usuario no encontrado: {responsible_name}")
            continue

        if pd.notna(row.get("Vicepresidencia")):
            user.area = str(row["Vicepresidencia"]).strip()
        if pd.notna(row.get("Área")):
            user.subarea = str(row["Área"]).strip()
        if pd.notna(row.get("Dirección")):
            user.direccion = str(row["Dirección"]).strip()
        if pd.notna(row.get("Linea")):
            user.linea = str(row["Linea"]).strip()
        if pd.notna(row.get("#Linea")):
            user.numero_linea = str(row["#Linea"]).strip()
        if pd.notna(row.get("Cargo")):
            user.position_name = str(row["Cargo"]).strip()

        indicator_name = str(row["Nombre del Indicador"]).strip()
        
        if month is None:
            for month_name, month_num in MONTHS_MAP.items():
                if pd.notna(row.get(month_name)):
                    month = month_num
                    break
            if month is None:
                month = 1

        existing = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.user_id == user.id,
            IndicatorAssignment.year == year,
            IndicatorAssignment.month == month,
            IndicatorAssignment.indicator_name == indicator_name
        ).first()

        if existing:
            existing.target_value = safe_float(row.get("Meta"))
            existing.weight = safe_float(row.get("Peso"))
            existing.formula = str(row.get("Formula del Indicador", "")) if pd.notna(row.get("Formula del Indicador")) else None
            existing.frequency = str(row.get("Frecuencia", "MONTHLY")) if pd.notna(row.get("Frecuencia")) else "MONTHLY"
            existing.year = year
            existing.month = month
            existing.position_name_at_assignment = str(row.get("Cargo", "")).strip() if pd.notna(row.get("Cargo")) else user.position_name
            existing.area_at_assignment = str(row.get("Vicepresidencia", "")).strip() if pd.notna(row.get("Vicepresidencia")) else user.area
            existing.subarea_at_assignment = str(row.get("Área", "")).strip() if pd.notna(row.get("Área")) else user.subarea
            existing.direccion_at_assignment = str(row.get("Dirección", "")).strip() if pd.notna(row.get("Dirección")) else user.direccion
            existing.linea_at_assignment = str(row.get("Linea", "")).strip() if pd.notna(row.get("Linea")) else user.linea
            existing.numero_linea_at_assignment = str(row.get("#Linea", "")).strip() if pd.notna(row.get("#Linea")) else user.numero_linea
            updated += 1
        else:
            assignment = IndicatorAssignment(
                user_id=user.id,
                indicator_name=indicator_name,
                formula=str(row.get("Formula del Indicador", "")) if pd.notna(row.get("Formula del Indicador")) else None,
                year=year,
                month=month,
                target_value=safe_float(row.get("Meta")),
                weight=safe_float(row.get("Peso")),
                frequency=str(row.get("Frecuencia", "MONTHLY")) if pd.notna(row.get("Frecuencia")) else "MONTHLY",
                position_name_at_assignment=str(row.get("Cargo", "")).strip() if pd.notna(row.get("Cargo")) else user.position_name,
                area_at_assignment=str(row.get("Vicepresidencia", "")).strip() if pd.notna(row.get("Vicepresidencia")) else user.area,
                subarea_at_assignment=str(row.get("Área", "")).strip() if pd.notna(row.get("Área")) else user.subarea,
                direccion_at_assignment=str(row.get("Dirección", "")).strip() if pd.notna(row.get("Dirección")) else user.direccion,
                linea_at_assignment=str(row.get("Linea", "")).strip() if pd.notna(row.get("Linea")) else user.linea,
                numero_linea_at_assignment=str(row.get("#Linea", "")).strip() if pd.notna(row.get("#Linea")) else user.numero_linea
            )
            db.add(assignment)
            created += 1

    db.commit()

    return {
        "created": created,
        "updated": updated
    }


# ------------------------------------------------
# CLONE FROM PREVIOUS MONTH
# ------------------------------------------------

def clone_from_previous_month(db: Session, year: int, month: int):
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1

    prev_assignments = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.year == prev_year,
        IndicatorAssignment.month == prev_month
    ).all()

    if not prev_assignments:
        return {"created": 0, "message": "No assignments found for previous month"}

    created = 0
    updated = 0

    for prev in prev_assignments:
        user = db.query(User).filter(User.id == prev.user_id).first()
        if not user:
            continue

        existing = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.user_id == prev.user_id,
            IndicatorAssignment.year == year,
            IndicatorAssignment.month == month,
            IndicatorAssignment.indicator_name == prev.indicator_name
        ).first()

        if existing:
            existing.target_value = prev.target_value
            existing.weight = prev.weight
            existing.formula = prev.formula
            existing.frequency = prev.frequency
            existing.position_name_at_assignment = user.position_name
            existing.area_at_assignment = user.area
            existing.subarea_at_assignment = user.subarea
            existing.direccion_at_assignment = user.direccion
            existing.linea_at_assignment = user.linea
            existing.numero_linea_at_assignment = user.numero_linea
            updated += 1
        else:
            assignment = IndicatorAssignment(
                user_id=prev.user_id,
                indicator_name=prev.indicator_name,
                formula=prev.formula,
                year=year,
                month=month,
                target_value=prev.target_value,
                weight=prev.weight,
                frequency=prev.frequency,
                position_name_at_assignment=user.position_name,
                area_at_assignment=user.area,
                subarea_at_assignment=user.subarea,
                direccion_at_assignment=user.direccion,
                linea_at_assignment=user.linea,
                numero_linea_at_assignment=user.numero_linea
            )
            db.add(assignment)
            created += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "message": f"Cloned assignments from {prev_month}/{prev_year} to {month}/{year}"
    }