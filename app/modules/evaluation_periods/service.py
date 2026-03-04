from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.models.evaluation_period import EvaluationPeriod
from app.models.evaluation import Evaluation
from app.models.user import User


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

def open_period(db: Session, period_id: UUID):
    period = db.get(EvaluationPeriod, period_id)

    if not period:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    if period.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Solo se puede abrir un periodo en DRAFT")

    # Obtener usuarios activos con líder
    users = db.scalars(
        select(User).where(
            User.is_active == True,
            User.leader_id.is_not(None)
        )
    ).all()

    evaluations = []

    for user in users:
        evaluations.append(
            Evaluation(
                evaluation_period_id=period.id,
                employee_id=user.id,
                evaluator_id=user.leader_id,
                status="PENDING",
            )
        )

    db.add_all(evaluations)

    period.status = "OPEN"

    db.commit()
    db.refresh(period)

    return period

def close_period(db: Session, period_id: UUID):
    period = db.get(EvaluationPeriod, period_id)

    if not period:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    if period.status != "OPEN":
        raise HTTPException(status_code=400, detail="Solo se puede cerrar un periodo abierto")

    period.status = "CLOSED"

    db.commit()
    db.refresh(period)

    return period