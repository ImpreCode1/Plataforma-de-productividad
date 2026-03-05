from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.core.security.dependencies import get_current_user
from .schemas import EvaluationResultUpdate, EvaluationResultResponse
from .service import update_result, get_my_assigned_evaluations

router = APIRouter()

@router.patch("/{result_id}", response_model=EvaluationResultResponse)
def update_evaluation_result(
    result_id: UUID,
    payload: EvaluationResultUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_result(
        db,
        result_id,
        payload.achieved_value,
        current_user,
    )
    
@router.get("/assigned")
def get_assigned(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_my_assigned_evaluations(db, current_user)