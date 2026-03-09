from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.indicator import PositionIndicator
from app.modules.position_indicators.schemas import (
    PositionIndicatorCreate,
    PositionIndicatorUpdate
)


# -----------------------------------------
# List
# -----------------------------------------

def get_position_indicators(db: Session):

    return db.query(PositionIndicator).all()


# -----------------------------------------
# Get
# -----------------------------------------

def get_position_indicator(db: Session, pi_id: UUID):

    pi = (
        db.query(PositionIndicator)
        .filter(PositionIndicator.id == pi_id)
        .first()
    )

    if not pi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position indicator not found"
        )

    return pi


# -----------------------------------------
# Create
# -----------------------------------------

def create_position_indicator(
    db: Session,
    pi_in: PositionIndicatorCreate
):

    pi = PositionIndicator(**pi_in.model_dump())

    db.add(pi)
    db.commit()
    db.refresh(pi)

    return pi


# -----------------------------------------
# Update
# -----------------------------------------

def update_position_indicator(
    db: Session,
    pi_id: UUID,
    pi_in: PositionIndicatorUpdate
):

    pi = get_position_indicator(db, pi_id)

    for field, value in pi_in.model_dump(exclude_unset=True).items():
        setattr(pi, field, value)

    db.commit()
    db.refresh(pi)

    return pi


# -----------------------------------------
# Delete
# -----------------------------------------

def delete_position_indicator(
    db: Session,
    pi_id: UUID
):

    pi = get_position_indicator(db, pi_id)

    db.delete(pi)
    db.commit()

    return pi