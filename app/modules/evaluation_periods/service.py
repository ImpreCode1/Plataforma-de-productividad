from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from fastapi import HTTPException

from app.models.evaluation_period import EvaluationPeriod
from app.models.evaluation import Evaluation
from app.models.evaluation_result import EvaluationResult
from app.models.user import User
from app.models.indicator import Indicator
from app.models.position_indicator import PositionIndicator
from app.models.user_indicator_override import UserIndicatorOverride

# =========================================================
# CREATE PERIOD
# =========================================================

def create_period(db: Session, name: str, start_date, end_date):

    period = EvaluationPeriod(
        name=name,
        start_date=start_date,
        end_date=end_date,
        status="DRAFT",
    )

    db.add(period)
    db.commit()
    db.refresh(period)

    return period


# =========================================================
# INTERNAL: GET APPLICABLE INDICATORS
# =========================================================

def _get_applicable_indicators(db: Session, user: User):

    # 1️⃣ Overrides por usuario
    override_indicators = db.scalars(
        select(Indicator)
        .join(UserIndicatorOverride)
        .where(UserIndicatorOverride.user_id == user.id)
    ).all()

    if override_indicators:
        return override_indicators

    # 2️⃣ Por posición
    if not user.position_id:
        raise HTTPException(
            status_code=400,
            detail=f"Usuario {user.id} no tiene posición asignada",
        )

    position_indicators = db.scalars(
        select(Indicator)
        .join(PositionIndicator)
        .where(PositionIndicator.position_id == user.position_id)
    ).all()

    return position_indicators


# =========================================================
# OPEN PERIOD (ENGINE INTEGRADO)
# =========================================================

def open_period(db: Session, period_id: UUID):

    period = db.get(EvaluationPeriod, period_id)

    if not period:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    if period.status != "DRAFT":
        raise HTTPException(
            status_code=400,
            detail="Solo se puede abrir un periodo en DRAFT",
        )

    # 🔒 Idempotencia
    existing = db.scalars(
        select(Evaluation).where(
            Evaluation.period_id == period.id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="El periodo ya tiene evaluaciones generadas",
        )

    users = db.scalars(
        select(User).where(
            User.is_active.is_(True),
            User.leader_id.is_not(None),
        )
    ).all()

    total_evaluations = 0
    total_results = 0

    for user in users:

        indicators = _get_applicable_indicators(db, user)

        evaluation = Evaluation(
            period_id=period.id,
            user_id=user.id,
            leader_id=user.leader_id,
            status="IN_PROGRESS",
        )

        db.add(evaluation)
        db.flush()

        total_evaluations += 1

        for indicator in indicators:
            result = EvaluationResult(
                evaluation_id=evaluation.id,
                indicator_id=indicator.id,
                score=None,
                comment=None,
            )
            db.add(result)
            total_results += 1

    period.status = "OPEN"

    db.commit()

    return {
        "period_id": str(period.id),
        "users_processed": len(users),
        "evaluations_created": total_evaluations,
        "results_created": total_results,
        "message": "Periodo abierto y evaluaciones generadas correctamente",
    }


# =========================================================
# CLOSE PERIOD
# =========================================================

def close_period(db: Session, period_id: UUID):

    period = db.get(EvaluationPeriod, period_id)

    if not period:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    if period.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden cerrar periodos OPEN",
        )

    evaluations = db.scalars(
        select(Evaluation).where(
            Evaluation.period_id == period.id
        )
    ).all()

    if not evaluations:
        raise HTTPException(
            status_code=400,
            detail="El periodo no tiene evaluaciones",
        )

    total_closed = 0

    for evaluation in evaluations:

        results = db.scalars(
            select(EvaluationResult).where(
                EvaluationResult.evaluation_id == evaluation.id
            )
        ).all()

        if not results:
            raise HTTPException(
                status_code=400,
                detail=f"La evaluación {evaluation.id} no tiene resultados",
            )

        # 🔒 Validar completitud
        if any(r.weighted_score is None for r in results):
            raise HTTPException(
                status_code=400,
                detail=f"La evaluación {evaluation.id} no está completa",
            )

        # 🧮 Calcular promedio final
        total_score = sum(float(r.weighted_score) for r in results)
        final_score = total_score / len(results)

        evaluation.final_score = round(final_score, 2)
        evaluation.status = "CLOSED"
        evaluation.closed_at = datetime.now()

        total_closed += 1

    period.status = "CLOSED"

    db.commit()

    return {
        "period_id": str(period.id),
        "evaluations_closed": total_closed,
        "message": "Periodo cerrado correctamente",
    }
    
# =====================================================
# LIST PERIODS
# =====================================================

def list_periods(db: Session):
    periods = db.scalars(
        select(EvaluationPeriod)
        .order_by(EvaluationPeriod.opened_at.desc())
    ).all()

    return periods


# =====================================================
# GET PERIOD DETAIL
# =====================================================

def get_period_detail(db: Session, period_id: UUID):
    period = db.get(EvaluationPeriod, period_id)

    if not period:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    # Métricas adicionales
    total_evaluations = db.scalar(
        select(func.count(Evaluation.id))
        .where(Evaluation.period_id == period.id)
    )

    closed_evaluations = db.scalar(
        select(func.count(Evaluation.id))
        .where(
            Evaluation.period_id == period.id,
            Evaluation.status == "CLOSED"
        )
    )

    return {
        "id": period.id,
        "name": period.year,
        "start_date": period.opened_at,
        "end_date": period.closed_at,
        "status": period.status,
        "total_evaluations": total_evaluations or 0,
        "closed_evaluations": closed_evaluations or 0,
    }
    
    