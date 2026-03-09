from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.modules.indicator_tracking.schemas import (
    IndicatorTrackingCreate,
    IndicatorTrackingUpdate,
    IndicatorTrackingResponse
)

from app.modules.indicator_tracking.service import IndicatorTrackingService

router = APIRouter(prefix="/indicator-tracking", tags=["Indicator Tracking"])


@router.post("/", response_model=IndicatorTrackingResponse)
def create_tracking(data: IndicatorTrackingCreate, db: Session = Depends(get_db)):

    return IndicatorTrackingService.create_tracking(db, data)


@router.get("/", response_model=list[IndicatorTrackingResponse])
def list_tracking(db: Session = Depends(get_db)):

    return IndicatorTrackingService.list_tracking(db)


@router.get("/{tracking_id}", response_model=IndicatorTrackingResponse)
def get_tracking(tracking_id: UUID, db: Session = Depends(get_db)):

    return IndicatorTrackingService.get_tracking(db, tracking_id)


@router.patch("/{tracking_id}", response_model=IndicatorTrackingResponse)
def update_tracking(
    tracking_id: UUID,
    data: IndicatorTrackingUpdate,
    db: Session = Depends(get_db)
):

    return IndicatorTrackingService.update_tracking(
        db,
        tracking_id,
        data.achieved_value
    )