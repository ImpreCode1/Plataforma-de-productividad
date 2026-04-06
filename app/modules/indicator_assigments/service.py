from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.indicator import Indicator
from app.modules.indicators.schemas import IndicatorCreate, IndicatorUpdate


# ---------------------------------
# List indicators
# ---------------------------------

def get_indicators(db: Session):

    return (
        db.query(Indicator)
        .order_by(Indicator.name)
        .all()
    )


# ---------------------------------
# Get indicator
# ---------------------------------

def get_indicator(db: Session, indicator_id: UUID):

    indicator = (
        db.query(Indicator)
        .filter(Indicator.id == indicator_id)
        .first()
    )

    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicator not found"
        )

    return indicator


# ---------------------------------
# Create indicator
# ---------------------------------

def create_indicator(
    db: Session,
    indicator_in: IndicatorCreate
):

    indicator = Indicator(**indicator_in.model_dump())

    db.add(indicator)
    db.commit()
    db.refresh(indicator)

    return indicator


# ---------------------------------
# Update indicator
# ---------------------------------

def update_indicator(
    db: Session,
    indicator_id: UUID,
    indicator_in: IndicatorUpdate
):

    indicator = get_indicator(db, indicator_id)

    for field, value in indicator_in.model_dump(exclude_unset=True).items():
        setattr(indicator, field, value)

    db.commit()
    db.refresh(indicator)

    return indicator


# ---------------------------------
# Delete indicator
# ---------------------------------

def delete_indicator(
    db: Session,
    indicator_id: UUID
):

    indicator = get_indicator(db, indicator_id)

    db.delete(indicator)
    db.commit()

    return indicator