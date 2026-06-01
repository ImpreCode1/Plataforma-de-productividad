from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class MonthData(BaseModel):
    month: int
    achieved_value: Optional[Decimal] = None
    achieved_total: Optional[Decimal] = None
    achievement_percentage: Optional[Decimal] = None
    status: Optional[str] = None
    is_closed: bool
    approval_status: Optional[str] = "PENDIENTE"
    rejection_comment: Optional[str] = None
    tracking_id: Optional[UUID] = None


class IndicatorDashboard(BaseModel):
    indicator_name: str
    formula: Optional[str] = None
    target_value: Decimal
    weight: Decimal
    months: List[MonthData]


class DashboardResponse(BaseModel):
    user_id: UUID
    year: int
    indicators: List[IndicatorDashboard]
    
class UserDashboard(BaseModel):
    user_id: UUID
    name: str
    email: Optional[str] = None
    position_name: Optional[str] = None
    indicators: list


class TeamDashboardResponse(BaseModel):
    leader_id: UUID
    year: int
    month: int | None = None
    team: list[UserDashboard]