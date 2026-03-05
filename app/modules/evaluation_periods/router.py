from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.modules.evaluation_periods import service
from app.modules.evaluation_periods.schemas import (
    EvaluationPeriodCreate,
    EvaluationPeriodResponse,
    PeriodOpenResponse,
    PeriodCloseResponse,
)
from app.core.security.dependencies import require_roles

router = APIRouter()


# =====================================================
# CREATE PERIOD
# =====================================================

@router.post(
    "/",
    response_model=EvaluationPeriodResponse,
    summary="Create evaluation period (ADMIN only)",
)
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


# =====================================================
# OPEN PERIOD (Generates evaluations + results)
# =====================================================

@router.patch(
    "/{period_id}/open",
    response_model=PeriodOpenResponse,
    summary="Open evaluation period and generate evaluations",
)
def open_period(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.open_period(db, period_id)


# =====================================================
# CLOSE PERIOD (Calculate final scores)
# =====================================================

@router.patch(
    "/{period_id}/close",
    response_model=PeriodCloseResponse,
    summary="Close evaluation period and finalize scores",
)
def close_period(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.close_period(db, period_id)