from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class EvidenceData(BaseModel):
    id: UUID
    file_path: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by: Optional[UUID] = None
    uploaded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class IndicatorTrackingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    assignment_id: UUID

    year: int
    month: int

    achieved_value: Optional[Decimal] = None
    achieved_total: Optional[Decimal] = None
    achievement_percentage: Optional[Decimal] = None
    weighted_score: Optional[Decimal] = None

    target_met: Optional[bool] = None
    status: Optional[str] = None
    is_closed: bool = False
    
    approval_status: Optional[str] = "PENDIENTE"
    submitted_at: Optional[datetime] = None
    submitted_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_comment: Optional[str] = None

    indicator_name: Optional[str] = None
    target_value: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    formula: Optional[str] = None
    
    evidence_count: int = 0
    evidences: List[EvidenceData] = []


class TrackingListResponse(BaseModel):
    tracking: List[IndicatorTrackingResponse]


class TrackingUpdateRequest(BaseModel):
    achieved_value: Decimal
    achieved_total: Optional[Decimal] = None


class TrackingCloseRequest(BaseModel):
    achieved_value: Optional[Decimal] = None
    achieved_total: Optional[Decimal] = None