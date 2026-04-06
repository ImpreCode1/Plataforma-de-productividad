from uuid import UUID
from pydantic import BaseModel
from datetime import datetime


class EvidenceResponse(BaseModel):
    id: UUID
    tracking_id: UUID
    file_path: str
    uploaded_by: UUID
    uploaded_at: datetime

    class Config:
        from_attributes = True