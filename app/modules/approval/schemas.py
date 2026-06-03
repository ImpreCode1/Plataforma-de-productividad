from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class TrackingSubmitRequest(BaseModel):
    reason_not_met: Optional[str] = None
    action_plan: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "reason_not_met": "Falta de recursos",
                "action_plan": "Solicitar equipo adicional para el próximo mes"
            }
        }


class AssignmentSubmitRequest(BaseModel):
    reason_not_met: Optional[str] = None
    action_plan: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "reason_not_met": "Falta de recursos",
                "action_plan": "Solicitar equipo adicional para el próximo mes"
            }
        }


class TrackingApproveRequest(BaseModel):
    pass


class TrackingRejectRequest(BaseModel):
    comment: str


class TrackingApprovalResponse(BaseModel):
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
    approval_status: str
    submitted_at: Optional[datetime] = None
    submitted_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_comment: Optional[str] = None

    class Config:
        from_attributes = True
