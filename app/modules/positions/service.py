from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.organization import Position
from app.modules.positions.schemas import PositionCreate, PositionUpdate


# -----------------------------------------
# List positions
# -----------------------------------------


def get_positions(db: Session):

    return db.query(Position).order_by(Position.name).all()


# -----------------------------------------
# Get position
# -----------------------------------------


def get_position(db: Session, position_id: UUID):

    position = db.query(Position).filter(Position.id == position_id).first()

    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
        )

    return position


# -----------------------------------------
# Create position
# -----------------------------------------


def create_position(db: Session, position_in: PositionCreate):

    position = Position(**position_in.model_dump())

    db.add(position)
    db.commit()
    db.refresh(position)

    return position


# -----------------------------------------
# Update position
# -----------------------------------------


def update_position(db: Session, position_id: UUID, position_in: PositionUpdate):

    position = get_position(db, position_id)

    for field, value in position_in.model_dump(exclude_unset=True).items():
        setattr(position, field, value)

    db.commit()
    db.refresh(position)

    return position


# -----------------------------------------
# Delete position
# -----------------------------------------


def delete_position(db: Session, position_id: UUID):

    position = get_position(db, position_id)

    db.delete(position)
    db.commit()

    return position
