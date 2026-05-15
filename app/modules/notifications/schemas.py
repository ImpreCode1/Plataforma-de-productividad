from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class UserInfo(BaseModel):
    id: str
    name: str
    email: str
    role: str


class NotificationSendRequest(BaseModel):
    recipient_type: str  # "all_leaders", "all_employees", "specific"
    recipient_ids: Optional[List[str]] = None
    template: str  # "evidence_reminder", "calification_reminder"
    month: int
    year: int


class NotificationSendResponse(BaseModel):
    sent_count: int
    failed_count: int
    message: str


class NotificationHistoryItem(BaseModel):
    id: str
    sent_at: str
    recipient_type: str
    template: str
    month: int
    year: int
    recipient_count: int