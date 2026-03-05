from sqlalchemy.orm import Session
from app.models.organization import Position
from app.modules.positions.schemas import PositionCreate, PositionUpdate
import uuid

def get_positions(db: Session):
    return db.query(Position).all()

def get_position(db: Session, position_id: uuid.UUID):
    return db.query(Position).filter(Position.id == position_id).first()

def create_position(db: Session, position_in: PositionCreate):
    position = Position(**position_in.dict())
    db.add(position)
    db.commit()
    db.refresh(position)
    return position

def update_position(db: Session, position_id: uuid.UUID, position_in: PositionUpdate):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        return None
    for field, value in position_in.dict(exclude_unset=True).items():
        setattr(position, field, value)
    db.commit()
    db.refresh(position)
    return position

def delete_position(db: Session, position_id: uuid.UUID):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        return None
    db.delete(position)
    db.commit()
    return position