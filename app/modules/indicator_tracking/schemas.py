from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal


class EvidenceData(BaseModel):
    id: UUID
    file_path: str
    
    class Config:
        from_attributes = True


class IndicatorTrackingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    assignment_id: UUID

    year: int
    month: int

    achieved_value: Optional[Decimal]
    achieved_total: Optional[Decimal]
    achievement_percentage: Optional[Decimal]
    weighted_score: Optional[Decimal]

    target_met: Optional[bool]
    status: Optional[str]
    is_closed: bool
    
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