from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ApprovalConfigCreate(BaseModel):
    config_type: str
    config_value: str
    load_mode: str


class ApprovalConfigUpdate(BaseModel):
    load_mode: str


class ApprovalConfigResponse(BaseModel):
    id: UUID
    config_type: str
    config_value: str
    load_mode: str
    is_active: bool
    created_by: Optional[UUID] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApprovalConfigListResponse(BaseModel):
    configs: List[ApprovalConfigResponse]


class LoadModeCheck(BaseModel):
    user_id: UUID
    load_mode: str
