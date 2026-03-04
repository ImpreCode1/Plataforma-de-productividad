from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.modules.evaluation_periods import service
from app.modules.evaluation_periods.schemas import (
    EvaluationPeriodCreate,
    EvaluationPeriodResponse,
)
from app.core.security.dependencies import require_roles

router = APIRouter()


@router.post("/", response_model=EvaluationPeriodResponse)
def create_period(
    payload: EvaluationPeriodCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.create_period(
        db,
        payload.name,
        payload.start_date,
        payload.end_date,
    )


@router.patch("/{period_id}/open", response_model=EvaluationPeriodResponse)
def open_period(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.open_period(db, period_id)


@router.patch("/{period_id}/close", response_model=EvaluationPeriodResponse)
def close_period(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.close_period(db, period_id)