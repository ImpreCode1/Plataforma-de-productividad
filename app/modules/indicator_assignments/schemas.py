from uuid import UUID
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class IndicatorAssignmentCreate(BaseModel):
    user_id: UUID
    indicator_name: str
    formula: Optional[str] = None
    year: int
    month: Optional[int] = None
    target_value: Decimal
    weight: Decimal
    frequency: str = "MONTHLY"


class IndicatorAssignmentUpdate(BaseModel):
    indicator_name: Optional[str] = None
    formula: Optional[str] = None
    target_value: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None
    month: Optional[int] = None


class IndicatorAssignmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    indicator_name: str
    formula: Optional[str] = None
    year: int
    month: Optional[int] = None
    target_value: Decimal
    weight: Decimal
    frequency: str
    is_active: bool
    position_name_at_assignment: Optional[str] = None
    area_at_assignment: Optional[str] = None
    subarea_at_assignment: Optional[str] = None
    direccion_at_assignment: Optional[str] = None
    linea_at_assignment: Optional[str] = None
    numero_linea_at_assignment: Optional[str] = None

    class Config:
        from_attributes = True


class IndicatorAssignmentListResponse(BaseModel):
    assignments: List[IndicatorAssignmentResponse]


class ImportAssignmentsResponse(BaseModel):
    created: int
    updated: int
    failed: List[dict] = Field(default_factory=list)
    message: Optional[str] = None


class IndicatorData(BaseModel):
    formula: Optional[str] = None
    target_value: Decimal
    weight: Decimal
    frequency: str = "MONTHLY"


class ReopenAssignmentRequest(BaseModel):
    month: int
    indicators: dict[str, IndicatorData]


class YearlyTrackingError(BaseModel):
    responsable: str
    correo: Optional[str] = None
    indicador: str
    motivo: str


class ImportYearlyAssignmentsResponse(BaseModel):
    assignments_created: int = 0
    trackings_created: int = 0
    users_created: int = 0
    users_matched: int = 0
    already_existed: int = 0
    without_data: int = 0
    failed: List[YearlyTrackingError] = Field(default_factory=list)