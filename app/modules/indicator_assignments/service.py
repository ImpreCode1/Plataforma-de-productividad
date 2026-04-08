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

    # Validar duplicado (user + year + name)
    existing = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.user_id == data.user_id,
        IndicatorAssignment.year == data.year,
        IndicatorAssignment.indicator_name == data.indicator_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Indicator already exists for this user/year")

    assignment = IndicatorAssignment(
        user_id=data.user_id,
        indicator_name=data.indicator_name,
        formula=data.formula,
        year=data.year,
        target_value=data.target_value,
        weight=data.weight,
        frequency=data.frequency
    )

    db.add(assignment)
    db.flush()

    # ------------------------------------------------
    # GENERAR 12 MESES 🔥🔥🔥
    # ------------------------------------------------

    trackings = []

    for month in range(1, 13):
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

    for field, value in data.model_dump(exclude_unset=True).items():
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

    # Obtener los tracking_ids primero
    trackings = db.query(IndicatorTracking).filter(
        IndicatorTracking.assignment_id == assignment_id
    ).all()
    
    tracking_ids = [t.id for t in trackings]

    # Eliminar evidencia y planes de acción relacionados
    if tracking_ids:
        from app.models.evidence import Evidence
        from app.models.action_plan import ActionPlan
        
        db.query(Evidence).filter(Evidence.tracking_id.in_(tracking_ids)).delete(synchronize_session=False)
        db.query(ActionPlan).filter(ActionPlan.tracking_id.in_(tracking_ids)).delete(synchronize_session=False)

    # Eliminar trackings relacionados
    db.query(IndicatorTracking).filter(
        IndicatorTracking.assignment_id == assignment_id
    ).delete()

    db.delete(assignment)
    db.commit()


# ------------------------------------------------
# IMPORT EXCEL 🔥
# ------------------------------------------------

def import_assignments_from_excel(db: Session, file, year: int):
    df = pd.read_excel(file)

    created = 0
    updated = 0
    assignments_dict = {}

    # Primera pasada: buscar usuarios por email
    users_by_email = {}
    all_users = db.query(User).all()
    for user in all_users:
        users_by_email[user.email.lower()] = user

    # Procesar indicadores
    for _, row in df.iterrows():
        responsible_email = str(row["Responsable"]).lower().strip()
        user = users_by_email.get(responsible_email)
        
        if not user:
            continue

        indicator_name = str(row["Nombre del Indicador"]).strip()
        
        # Buscar si ya existe
        existing = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.user_id == user.id,
            IndicatorAssignment.year == year,
            IndicatorAssignment.indicator_name == indicator_name
        ).first()

        if existing:
            # Actualizar
            existing.target_value = float(row.get("Meta", 0))
            existing.weight = float(row.get("Peso", 0))
            existing.formula = str(row.get("Formula del Indicador", "")) if pd.notna(row.get("Formula del Indicador")) else None
            existing.frequency = str(row.get("Frecuencia", "MONTHLY")) if pd.notna(row.get("Frecuencia")) else "MONTHLY"
            updated += 1
        else:
            # Crear nuevo
            assignment = IndicatorAssignment(
                user_id=user.id,
                indicator_name=indicator_name,
                formula=str(row.get("Formula del Indicador", "")) if pd.notna(row.get("Formula del Indicador")) else None,
                year=year,
                target_value=float(row.get("Meta", 0)),
                weight=float(row.get("Peso", 0)),
                frequency=str(row.get("Frecuencia", "MONTHLY")) if pd.notna(row.get("Frecuencia")) else "MONTHLY"
            )
            db.add(assignment)
            assignments_dict[(user.id, indicator_name)] = assignment
            created += 1

    db.flush()

    # Segunda pasada: generar trackings para nuevos
    for (user_id, indicator_name), assignment in assignments_dict.items():
        for month in range(1, 13):
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