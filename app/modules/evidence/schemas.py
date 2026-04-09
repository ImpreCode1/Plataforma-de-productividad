from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EvidenceResponse(BaseModel):
    id: UUID
    tracking_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    year: Optional[int] = None
    month: Optional[int] = None
    file_path: str
    uploaded_by: UUID
    uploaded_at: datetime

    class Config:
        from_attributes = True