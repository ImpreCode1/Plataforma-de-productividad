from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.modules.positions.schemas import PositionCreate, PositionUpdate, PositionResponse
from app.modules.positions import service

router = APIRouter(
    prefix="/positions",
    tags=["Positions"]
)

@router.get("/", response_model=list[PositionResponse])
def list_positions(db: Session = Depends(get_db)):
    return service.get_positions(db)

@router.post("/", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
def create_position(position_in: PositionCreate, db: Session = Depends(get_db)):
    return service.create_position(db, position_in)

@router.patch("/{position_id}", response_model=PositionResponse)
def update_position(position_id: UUID, position_in: PositionUpdate, db: Session = Depends(get_db)):
    position = service.update_position(db, position_id, position_in)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position

@router.delete("/{position_id}", response_model=PositionResponse)
def delete_position(position_id: UUID, db: Session = Depends(get_db)):
    position = service.delete_position(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position