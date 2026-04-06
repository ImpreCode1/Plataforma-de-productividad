from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.indicator_assignment import IndicatorAssignment
from app.models.tracking import IndicatorTracking


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
        year=data.year,
        target_value=data.target_value,
        weight=data.weight
    )

    db.add(assignment)
    db.flush()  # 🔥 necesitamos el ID sin commit

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
# UPDATE
# ------------------------------------------------

def update_assignment(db: Session, assignment_id: UUID, data):
    assignment = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    for field, value in data.dict(exclude_unset=True).items():
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

    db.delete(assignment)
    db.commit()