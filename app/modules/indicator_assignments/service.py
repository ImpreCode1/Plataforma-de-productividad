from sqlalchemy.orm import Session
from uuid import UUID
import uuid
from fastapi import HTTPException
import pandas as pd
import re
import unicodedata

from app.models.indicator_assignment import IndicatorAssignment
from app.models.tracking import IndicatorTracking
from app.models.user import User
from app.models.role import Role, UserRole


def normalize_name(name):
    if not name:
        return name
    name = str(name)
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", name.strip()).lower()


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
        str_value = str(value).strip()
        if str_value.endswith('%'):
            str_value = str_value[:-1].replace(',', '.')
            return float(str_value)
        float_val = float(value)
        if 0 < float_val <= 1:
            return round(float_val * 100, 2)
        return round(float_val, 2)
    except:
        return default


def import_assignments_from_excel(db: Session, file, year: int, month: int = None):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()

    created = 0
    updated = 0
    failed = []

    users_by_name = {}
    all_users = db.query(User).all()
    for user in all_users:
        normalized = normalize_name(user.name)
        users_by_name[normalized] = user

    for _, row in df.iterrows():
        responsible_name = str(row["Responsable"]).strip()
        normalized_name = normalize_name(responsible_name)
        user = users_by_name.get(normalized_name)

        if not user:
            user = find_user_by_fuzzy_name(users_by_name, responsible_name)

        if not user:
            indicator_name = str(row.get("Nombre del Indicador", "")).strip()
            failed.append({
                "responsable": responsible_name,
                "indicador": indicator_name
            })
            continue

        if pd.notna(row.get("Vicepresidencia")):
            user.area = str(row["Vicepresidencia"]).strip()
        if pd.notna(row.get("Área")):
            user.subarea = str(row["Área"]).strip()
        if pd.notna(row.get("Dirección")):
            user.direccion = str(row["Dirección"]).strip()
        if pd.notna(row.get("Linea")):
            user.linea = str(row["Linea"]).strip()
        if pd.notna(row.get("# Linea")):
            user.numero_linea = str(row["# Linea"]).strip()
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
            existing.numero_linea_at_assignment = str(row.get("# Linea", "")).strip() if pd.notna(row.get("# Linea")) else user.numero_linea
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
                numero_linea_at_assignment=str(row.get("# Linea", "")).strip() if pd.notna(row.get("# Linea")) else user.numero_linea
            )
            db.add(assignment)
            created += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "failed": failed
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


# ------------------------------------------------
# IMPORT EXCEL YEARLY (2025) 🔥
# ------------------------------------------------

MONTH_COLUMNS = [
    ("Enero", "Logro Enero", 1),
    ("Febrero", "Logro Febrero", 2),
    ("Marzo", "Logro Marzo", 3),
    ("Abril", "Logro Abril", 4),
    ("Mayo", "Logro Mayo", 5),
    ("Junio", "Logro Junio", 6),
    ("Julio", "Logro Julio", 7),
    ("Agosto", "Logro Agosto", 8),
    ("Septiembre", "Logro Septiembre", 9),
    ("Octubre", "Logro Octubre", 10),
    ("Noviembre", "Logro Noviembre", 11),
    ("Diciembre", "Logro Diciembre", 12),
]


def parse_achieved_value(value):
    if value is None or pd.isna(value):
        return None, None
    
    str_val = str(value).strip()
    if str_val in ("", "-", "N/A", "NA", "n/a"):
        return None, None
    
    parts = str_val.split("/")
    if len(parts) == 2:
        try:
            num = float(parts[0].strip())
            den = float(parts[1].strip())
            if den != 0:
                return num, den
        except:
            pass
    
    parsed = safe_float(value, default=None)
    if parsed is not None:
        return parsed, None
    
    return None, None


def import_yearly_assignments_from_excel(db: Session, file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    
    assignments_created = 0
    trackings_created = 0
    users_created = 0
    users_matched = 0
    already_existed = 0
    without_data = 0
    failed = []
    
    users_by_email = {}
    users_by_name = {}
    all_users = db.query(User).all()
    for user in all_users:
        if user.email:
            users_by_email[user.email.strip().lower()] = user
        normalized = normalize_name(user.name)
        users_by_name[normalized] = user
    
    employee_role = db.query(Role).filter(Role.name == "EMPLOYEE").first()
    if not employee_role:
        raise HTTPException(status_code=500, detail="Role EMPLOYEE not found in database")
    
    for _, row in df.iterrows():
        email = str(row.get("Correo Corporativo", "")).strip().lower() if pd.notna(row.get("Correo Corporativo")) else ""
        responsible_name = str(row.get("Responsable", "")).strip() if pd.notna(row.get("Responsable")) else ""
        indicator_name = str(row.get("Nombre del Indicador", "")).strip() if pd.notna(row.get("Nombre del Indicador")) else ""

        if not indicator_name:
            failed.append({
                "responsable": responsible_name,
                "correo": email or None,
                "indicador": "",
                "motivo": "Nombre del indicador vacío"
            })
            continue

        user = None

        if email and email in users_by_email:
            user = users_by_email[email]
            users_by_name[normalize_name(user.name)] = user

        if not user and responsible_name:
            user = find_user_by_fuzzy_name(users_by_name, responsible_name)

        if not user and email:
            existing_by_email = db.query(User).filter(User.email == email).first()
            if existing_by_email:
                user = existing_by_email
                users_by_email[email] = user
                users_by_name[normalize_name(user.name)] = user

        if not user:
            doc_number = f"EXT-{uuid.uuid4()}"
            user = User(
                document_number=doc_number,
                name=responsible_name if responsible_name else email.split("@")[0],
                email=email if email else f"ext-{uuid.uuid4()}@external.com",
                position_name=str(row.get("Cargo", "")).strip() if pd.notna(row.get("Cargo")) else None,
                area=str(row.get("Vicepresidencia", "")).strip() if pd.notna(row.get("Vicepresidencia")) else None,
                subarea=str(row.get("Área", "")).strip() if pd.notna(row.get("Área")) else None,
                direccion=str(row.get("Dirección", "")).strip() if pd.notna(row.get("Dirección")) else None,
                linea=str(row.get("Linea", "")).strip() if pd.notna(row.get("Linea")) else None,
                numero_linea=str(row.get("# Linea", "")).strip() if pd.notna(row.get("# Linea")) else None,
                is_active=False,
            )
            db.add(user)
            db.flush()

            existing_ur = db.query(UserRole).filter(
                UserRole.user_id == user.id,
                UserRole.role_id == employee_role.id
            ).first()
            if not existing_ur:
                db.add(UserRole(user_id=user.id, role_id=employee_role.id))

            users_by_email[user.email.strip().lower()] = user
            users_by_name[normalize_name(user.name)] = user
            users_created += 1
        else:
            users_matched += 1

        target_value = safe_float(row.get("Meta"), default=0)
        weight = safe_float(row.get("Peso"), default=0)
        frequency = str(row.get("Frecuencia", "MONTHLY")).strip() if pd.notna(row.get("Frecuencia")) else "MONTHLY"

        if pd.notna(row.get("Vicepresidencia")):
            user.area = str(row["Vicepresidencia"]).strip()
        if pd.notna(row.get("Área")):
            user.subarea = str(row["Área"]).strip()
        if pd.notna(row.get("Dirección")):
            user.direccion = str(row["Dirección"]).strip()
        if pd.notna(row.get("Linea")):
            user.linea = str(row["Linea"]).strip()
        if pd.notna(row.get("# Linea")):
            user.numero_linea = str(row["# Linea"]).strip()
        if pd.notna(row.get("Cargo")):
            user.position_name = str(row["Cargo"]).strip()

        area_snapshot = str(row.get("Vicepresidencia", "")).strip() if pd.notna(row.get("Vicepresidencia")) else user.area
        subarea_snapshot = str(row.get("Área", "")).strip() if pd.notna(row.get("Área")) else user.subarea
        direccion_snapshot = str(row.get("Dirección", "")).strip() if pd.notna(row.get("Dirección")) else user.direccion
        linea_snapshot = str(row.get("Linea", "")).strip() if pd.notna(row.get("Linea")) else user.linea
        numero_linea_snapshot = str(row.get("# Linea", "")).strip() if pd.notna(row.get("# Linea")) else user.numero_linea
        cargo_snapshot = str(row.get("Cargo", "")).strip() if pd.notna(row.get("Cargo")) else user.position_name

        had_any_data = False

        for month_name, logro_name, month_num in MONTH_COLUMNS:
            achieved_value, achieved_total = parse_achieved_value(row.get(month_name))
            logro_value = safe_float(row.get(logro_name), default=None) if pd.notna(row.get(logro_name)) else None

            if achieved_value is None and logro_value is None:
                continue

            had_any_data = True

            existing_assignment = db.query(IndicatorAssignment).filter(
                IndicatorAssignment.user_id == user.id,
                IndicatorAssignment.year == 2025,
                IndicatorAssignment.month == month_num,
                IndicatorAssignment.indicator_name == indicator_name,
            ).first()

            if existing_assignment:
                existing_assignment.target_value = target_value
                existing_assignment.weight = weight
                existing_assignment.frequency = frequency
                existing_assignment.position_name_at_assignment = cargo_snapshot
                existing_assignment.area_at_assignment = area_snapshot
                existing_assignment.subarea_at_assignment = subarea_snapshot
                existing_assignment.direccion_at_assignment = direccion_snapshot
                existing_assignment.linea_at_assignment = linea_snapshot
                existing_assignment.numero_linea_at_assignment = numero_linea_snapshot
                assignment = existing_assignment
                already_existed += 1
            else:
                assignment = IndicatorAssignment(
                    user_id=user.id,
                    indicator_name=indicator_name,
                    formula=None,
                    year=2025,
                    month=month_num,
                    target_value=target_value,
                    weight=weight,
                    frequency=frequency,
                    position_name_at_assignment=cargo_snapshot,
                    area_at_assignment=area_snapshot,
                    subarea_at_assignment=subarea_snapshot,
                    direccion_at_assignment=direccion_snapshot,
                    linea_at_assignment=linea_snapshot,
                    numero_linea_at_assignment=numero_linea_snapshot,
                )
                db.add(assignment)
                db.flush()
                assignments_created += 1

            existing_tracking = db.query(IndicatorTracking).filter(
                IndicatorTracking.assignment_id == assignment.id,
                IndicatorTracking.year == 2025,
                IndicatorTracking.month == month_num,
            ).first()

            if existing_tracking:
                existing_tracking.achieved_value = achieved_value
                existing_tracking.achieved_total = achieved_total
                existing_tracking.weighted_score = logro_value
                existing_tracking.target_met = logro_value is not None
                if achieved_value is not None and achieved_total is not None and achieved_total != 0:
                    existing_tracking.achievement_percentage = round((achieved_value / achieved_total) * 100, 2)
                elif achieved_value is not None:
                    existing_tracking.achievement_percentage = achieved_value
            else:
                tracking = IndicatorTracking(
                    user_id=user.id,
                    assignment_id=assignment.id,
                    year=2025,
                    month=month_num,
                    achieved_value=achieved_value,
                    achieved_total=achieved_total,
                    weighted_score=logro_value,
                    target_met=logro_value is not None,
                    status="CLOSED",
                    is_closed=True,
                    approval_status="APROBADO",
                )
                if achieved_value is not None and achieved_total is not None and achieved_total != 0:
                    tracking.achievement_percentage = round((achieved_value / achieved_total) * 100, 2)
                elif achieved_value is not None:
                    tracking.achievement_percentage = achieved_value
                db.add(tracking)
                trackings_created += 1

        if not had_any_data:
            without_data += 1

    db.commit()

    return {
        "assignments_created": assignments_created,
        "trackings_created": trackings_created,
        "users_created": users_created,
        "users_matched": users_matched,
        "already_existed": already_existed,
        "without_data": without_data,
        "failed": failed,
    }