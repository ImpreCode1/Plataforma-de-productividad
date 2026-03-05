from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class EvaluationPeriodCreate(BaseModel):
    name: str
    start_date: date
    end_date: date


class EvaluationPeriodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    start_date: date
    end_date: date
    status: str
    created_at: datetime
    
class PeriodOpenResponse(BaseModel):
    period_id: UUID
    users_processed: int
    evaluations_created: int
    results_created: int
    message: str


class PeriodCloseResponse(BaseModel):
    period_id: UUID
    evaluations_closed: int
    message: str
    
class EvaluationPeriodDetailResponse(BaseModel):
    id: UUID
    name: str
    start_date: date
    end_date: date
    status: str
    total_evaluations: int
    closed_evaluations: int