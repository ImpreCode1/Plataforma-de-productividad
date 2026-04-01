from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class EvidenceCreate(BaseModel):
    indicator_tracking_id: UUID
    file_path: str


class EvidenceResponse(BaseModel):
    id: UUID
    indicator_tracking_id: UUID
    file_path: str
    uploaded_by: UUID
    uploaded_at: datetime
    status: str = "pending"
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EvidenceReviewRequest(BaseModel):
    status: str


class EvidenceReviewResponse(BaseModel):
    id: UUID
    indicator_tracking_id: UUID
    file_path: str
    uploaded_by: UUID
    uploaded_at: datetime
    status: str
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True