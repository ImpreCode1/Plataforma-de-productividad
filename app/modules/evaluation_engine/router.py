from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.evaluation_engine import service
from app.modules.evaluation_engine.schemas import GenerationResponse
from app.core.security.dependencies import require_roles

router = APIRouter()


@router.post(
    "/{period_id}/generate",
    response_model=GenerationResponse,
)
def generate_evaluations(
    period_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("ADMIN")),
):
    return service.generate_for_period(db, period_id)