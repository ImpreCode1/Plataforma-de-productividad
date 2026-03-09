from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class EvidenceCreate(BaseModel):
    indicator_tracking_id: UUID
    file_path: str


class EvidenceResponse(BaseModel):
    id: UUID
    indicator_tracking_id: UUID
    file_path: str
    uploaded_by: UUID
    uploaded_at: datetime

    class Config:
        from_attributes = True