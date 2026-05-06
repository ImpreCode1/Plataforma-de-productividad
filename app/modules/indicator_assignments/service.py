from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
import pandas as pd

from app.models.indicator_assignment import IndicatorAssignment
from app.models.tracking import IndicatorTracking
from app.models.user import User


# ------------------------------------------------
# CREATE + GENERATE MONTHS 🔥
# ------------------------------------------------

def create_assignment(db: Session, data):
    from datetime import datetime

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.user_id == data.user_id,
        IndicatorAssignment.year == data.year,
        IndicatorAssignment.indicator_name == data.indicator_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Indicator already exists for this user/year")

    current_month = datetime.now().month if data.year == datetime.now().year else 1
    start_month = data.start_month if data.start_month is not None else current_month
    end_month = data.end_month if data.end_month is not None else 12
    if start_month > end_month:
        raise HTTPException(status_code=400, detail="start_month must be <= end_month")

    assignment = IndicatorAssignment(
        user_id=data.user_id,
        indicator_name=data.indicator_name,
        formula=data.formula,
        year=data.year,
        target_value=data.target_value,
        weight=data.weight,
        frequency=data.frequency,
        start_month=start_month,
        end_month=end_month,
        position_name_at_assignment=user.position_name,
        area_at_assignment=user.area,
        subarea_at_assignment=user.subarea
    )

    db.add(assignment)
    db.flush()

    trackings = []

    for month in range(start_month, end_month + 1):
        tracking = IndicatorTracking(
            user_id=data.user_id,
            assignment_id=assignment.id,
            year=data.year,
            month=month,
            status="PENDING",
            is_closed=False
        )
        trackings.append(tracking)

    db.add_all(trackings)

    db.commit()
    db.refresh(assignment)

    return assignment


# ------------------------------------------------
# LIST
# ------------------------------------------------

def list_assignments(db: Session, user_id: UUID, year: int):
    return db.query(IndicatorAssignment).filter(
        IndicatorAssignment.user_id == user_id,
        IndicatorAssignment.year == year
    ).all()


# ------------------------------------------------
# LIST ALL
# ------------------------------------------------

def list_all_assignments(db: Session, year: int | None = None):
    query = db.query(IndicatorAssignment)
    if year:
        query = query.filter(IndicatorAssignment.year == year)
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

    old_end_month = assignment.end_month

    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(assignment, field, value)

    if data.end_month and data.end_month > old_end_month:
        existing_months = db.query(IndicatorTracking).filter(
            IndicatorTracking.assignment_id == assignment_id
        ).all()
        existing_months_set = {t.month for t in existing_months}

        for month in range(old_end_month + 1, data.end_month + 1):
            if month not in existing_months_set:
                tracking = IndicatorTracking(
                    user_id=assignment.user_id,
                    assignment_id=assignment.id,
                    year=assignment.year,
                    month=month,
                    status="PENDING",
                    is_closed=False
                )
                db.add(tracking)

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
# CLOSE ASSIGNMENT (for position changes)
# ------------------------------------------------

def close_assignment(db: Session, assignment_id: UUID, close_month: int):
    assignment = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if close_month < assignment.start_month or close_month > assignment.end_month:
        raise HTTPException(status_code=400, detail="close_month must be between start_month and end_month")

    assignment.end_month = close_month

    trackings = db.query(IndicatorTracking).filter(
        IndicatorTracking.assignment_id == assignment_id,
        IndicatorTracking.month > close_month
    ).all()

    for tracking in trackings:
        db.delete(tracking)

    db.commit()
    db.refresh(assignment)
    return assignment


# ------------------------------------------------
# REOPEN ASSIGNMENT (create new with updated position)
# ------------------------------------------------

def reopen_assignment(db: Session, assignment_id: UUID, new_start_month: int, new_indicators: dict):
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
            IndicatorAssignment.indicator_name == indicator_name,
            IndicatorAssignment.start_month == new_start_month
        ).first()

        if existing:
            continue

        assignment = IndicatorAssignment(
            user_id=original.user_id,
            indicator_name=indicator_name,
            formula=values.get("formula"),
            year=original.year,
            target_value=values["target_value"],
            weight=values["weight"],
            frequency=values.get("frequency", "MONTHLY"),
            start_month=new_start_month,
            end_month=12,
            position_name_at_assignment=user.position_name,
            area_at_assignment=user.area,
            subarea_at_assignment=user.subarea
        )
        db.add(assignment)
        created_assignments.append((assignment, new_start_month))

    db.flush()

    for assignment, start_m in created_assignments:
        for month in range(start_m, 13):
            tracking = IndicatorTracking(
                user_id=assignment.user_id,
                assignment_id=assignment.id,
                year=assignment.year,
                month=month,
                status="PENDING",
                is_closed=False
            )
            db.add(tracking)

    db.commit()
    return created_assignments


# ------------------------------------------------
# IMPORT EXCEL 🔥
# ------------------------------------------------

def import_assignments_from_excel(db: Session, file, year: int):
    from datetime import datetime

    df = pd.read_excel(file)

    created = 0
    updated = 0
    assignments_dict = {}

    users_by_name = {}
    all_users = db.query(User).all()
    for user in all_users:
        users_by_name[user.name.lower().strip()] = user

    for _, row in df.iterrows():
        responsible_name = str(row["Responsable"]).lower().strip()
        user = users_by_name.get(responsible_name)
        
        if not user:
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
        
        existing = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.user_id == user.id,
            IndicatorAssignment.year == year,
            IndicatorAssignment.indicator_name == indicator_name
        ).first()

        if existing:
            existing.target_value = float(row.get("Meta", 0))
            existing.weight = float(row.get("Peso", 0))
            existing.formula = str(row.get("Formula del Indicador", "")) if pd.notna(row.get("Formula del Indicador")) else None
            existing.frequency = str(row.get("Frecuencia", "MONTHLY")) if pd.notna(row.get("Frecuencia")) else "MONTHLY"
            updated += 1
        else:
            start_month = int(row.get("Mes Inicio", 1)) if pd.notna(row.get("Mes Inicio")) else 1
            end_month = int(row.get("Mes Fin", 12)) if pd.notna(row.get("Mes Fin")) else 12
            
            if start_month > end_month:
                start_month = 1
                end_month = 12

            assignment = IndicatorAssignment(
                user_id=user.id,
                indicator_name=indicator_name,
                formula=str(row.get("Formula del Indicador", "")) if pd.notna(row.get("Formula del Indicador")) else None,
                year=year,
                target_value=float(row.get("Meta", 0)),
                weight=float(row.get("Peso", 0)),
                frequency=str(row.get("Frecuencia", "MONTHLY")) if pd.notna(row.get("Frecuencia")) else "MONTHLY",
                start_month=start_month,
                end_month=end_month,
                position_name_at_assignment=str(row.get("Cargo", "").strip()) if pd.notna(row.get("Cargo")) else user.position_name,
                area_at_assignment=str(row.get("Vicepresidencia", "").strip()) if pd.notna(row.get("Vicepresidencia")) else user.area,
                subarea_at_assignment=str(row.get("Área", "").strip()) if pd.notna(row.get("Área")) else user.subarea,
                direccion_at_assignment=str(row.get("Dirección", "").strip()) if pd.notna(row.get("Dirección")) else user.direccion,
                linea_at_assignment=str(row.get("Linea", "").strip()) if pd.notna(row.get("Linea")) else user.linea,
                numero_linea_at_assignment=str(row.get("#Linea", "").strip()) if pd.notna(row.get("#Linea")) else user.numero_linea
            )
            db.add(assignment)
            assignments_dict[(user.id, indicator_name)] = assignment
            created += 1

    db.flush()

    for (user_id, indicator_name), assignment in assignments_dict.items():
        for month in range(assignment.start_month, assignment.end_month + 1):
            tracking = IndicatorTracking(
                user_id=user_id,
                assignment_id=assignment.id,
                year=year,
                month=month,
                status="PENDING",
                is_closed=False
            )
            db.add(tracking)

    db.commit()

    return {
        "created": created,
        "updated": updated
    }