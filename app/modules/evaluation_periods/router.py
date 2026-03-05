from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.session import get_db
from app.modules.evaluation_periods import service
from app.modules.evaluation_periods.schemas import (
    EvaluationPeriodCreate,
    EvaluationPeriodResponse,
    EvaluationPeriodDetailResponse,
    PeriodOpenResponse,
    PeriodCloseResponse,
)
from app.core.security.dependencies import require_roles

router = APIRouter()


# =====================================================
# CREATE
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
# LIST
# =====================================================

@router.get(
    "/",
    response_model=List[EvaluationPeriodResponse],
    summary="List all evaluation periods",
)
def list_periods(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.list_periods(db)


# =====================================================
# DETAIL
# =====================================================

@router.get(
    "/{period_id}",
    response_model=EvaluationPeriodDetailResponse,
    summary="Get evaluation period detail",
)
def get_period_detail(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.get_period_detail(db, period_id)


# =====================================================
# OPEN
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
# CLOSE
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