from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.evaluation_result import EvaluationResult
from app.models.evaluation_period import EvaluationPeriod
from app.models.indicator import Indicator
from app.models.position_indicator import PositionIndicator
from app.models.user_indicator_override import UserIndicatorOverride


def get_applicable_indicators(db: Session, user: User):
    """
    Determina indicadores aplicables:
    1. Overrides por usuario
    2. Si no hay, por posición
    """

    # 1️⃣ Overrides
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


def generate_for_period(db: Session, period_id: UUID):
    """
    Motor principal de generación automática.
    """

    period = db.get(EvaluationPeriod, period_id)

    if not period:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    if period.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="El periodo debe estar OPEN para generar evaluaciones",
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
            detail="Las evaluaciones ya fueron generadas para este periodo",
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

        indicators = get_applicable_indicators(db, user)

        evaluation = Evaluation(
            period_id=period.id,
            user_id=user.id,
            leader_id=user.leader_id,
            status="IN_PROGRESS",  # consistente con tu modelo
        )

        db.add(evaluation)
        db.flush()  # Obtener ID sin commit

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

    db.commit()

    return {
        "period_id": str(period.id),
        "total_users_processed": len(users),
        "total_evaluations_created": total_evaluations,
        "total_results_created": total_results,
        "message": "Evaluaciones generadas correctamente",
    }
    
from datetime import datetime
from sqlalchemy import func


def close_period(db: Session, period_id: UUID):
    """
    Cierra un periodo:
    - Verifica que todas las evaluaciones estén completas
    - Calcula final_score
    - Marca evaluaciones como CLOSED
    - Marca periodo como CLOSED
    """

    period = db.get(EvaluationPeriod, period_id)

    if not period:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    if period.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden cerrar periodos OPEN",
        )

    evaluations = db.scalars(
        select(Evaluation).where(Evaluation.period_id == period.id)
    ).all()

    if not evaluations:
        raise HTTPException(
            status_code=400,
            detail="El periodo no tiene evaluaciones generadas",
        )

    total_closed = 0

    for evaluation in evaluations:

        results = db.scalars(
            select(EvaluationResult).where(
                EvaluationResult.evaluation_id == evaluation.id
            )
        ).all()

        # 🔒 Validar que todos tengan score
        if any(r.weighted_score is None for r in results):
            raise HTTPException(
                status_code=400,
                detail=f"La evaluación {evaluation.id} no está completa",
            )

        # 🧮 Calcular promedio
        total_score = sum(float(r.weighted_score) for r in results)
        final_score = total_score / len(results)

        evaluation.final_score = round(final_score, 2)
        evaluation.status = "CLOSED"
        evaluation.closed_at = datetime.now()

        total_closed += 1

    # 🔐 Cerrar periodo
    period.status = "CLOSED"

    db.commit()

    return {
        "period_id": str(period.id),
        "total_evaluations_closed": total_closed,
        "message": "Periodo cerrado correctamente",
    }