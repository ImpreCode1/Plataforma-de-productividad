from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EvidenceResponse(BaseModel):
    id: UUID
    tracking_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    year: Optional[int] = None
    month: Optional[int] = None
    file_path: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by: Optional[UUID] = None
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EvidenceListResponse(BaseModel):
    evidences: List[EvidenceResponse]


class EvidenceUploadResponse(BaseModel):
    id: UUID
    file_path: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: Optional[datetime] = None


class SetValueRequest(BaseModel):
    achieved_value: Decimal
    achieved_total: Optional[Decimal] = None