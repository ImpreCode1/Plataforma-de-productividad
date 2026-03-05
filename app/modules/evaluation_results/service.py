from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from app.models.evaluation_result import EvaluationResult
from app.models.evaluation import Evaluation
from app.models.indicator import Indicator


def update_result(
    db: Session,
    result_id: UUID,
    achieved_value: Decimal,
    current_user,
):
    """
    Permite al líder registrar el valor logrado para un indicador.
    Calcula automáticamente:
    - achievement_percentage
    - weighted_score
    """

    # 🔎 Obtener resultado
    result = db.get(EvaluationResult, result_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Resultado no encontrado",
        )

    # 🔎 Obtener evaluación
    evaluation = db.get(Evaluation, result.evaluation_id)

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="Evaluación no encontrada",
        )

    # 🔒 No permitir modificar evaluaciones cerradas
    if evaluation.status == "CLOSED":
        raise HTTPException(
            status_code=400,
            detail="La evaluación está cerrada",
        )

    # 🔐 Validar que el usuario sea el líder asignado
    if evaluation.leader_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para evaluar este usuario",
        )

    # 🔎 Obtener indicador
    indicator = db.get(Indicator, result.indicator_id)

    if not indicator:
        raise HTTPException(
            status_code=404,
            detail="Indicador no encontrado",
        )

    if indicator.target_value == 0:
        raise HTTPException(
            status_code=400,
            detail="El indicador tiene meta inválida (0)",
        )

    # 🧮 Cálculo profesional usando Decimal
    achievement_percentage = (
        achieved_value / indicator.target_value
    ) * Decimal("100")

    weighted_score = (
        achievement_percentage * indicator.weight
    ) / Decimal("100")

    # 🔢 Redondeo contable
    achievement_percentage = achievement_percentage.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    weighted_score = weighted_score.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    # 💾 Guardar valores
    result.achieved_value = achieved_value
    result.achievement_percentage = achievement_percentage
    result.weighted_score = weighted_score

    db.commit()
    db.refresh(result)

    return result

def get_my_assigned_evaluations(db: Session, current_user):

    evaluations = db.scalars(
        select(Evaluation).where(
            Evaluation.leader_id == current_user.id,
            Evaluation.status == "IN_PROGRESS",
        )
    ).all()

    return evaluations