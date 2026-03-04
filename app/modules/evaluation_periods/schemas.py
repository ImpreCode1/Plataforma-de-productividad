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