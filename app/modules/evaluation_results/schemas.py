from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal


class EvaluationResultUpdate(BaseModel):
    achieved_value: Decimal


class EvaluationResultResponse(BaseModel):
    id: UUID
    evaluation_id: UUID
    indicator_id: UUID
    achieved_value: Decimal
    achievement_percentage: Decimal
    weighted_score: Decimal

    class Config:
        from_attributes = True