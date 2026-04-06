from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class MonthData(BaseModel):
    month: int
    achieved_value: Optional[Decimal]
    achievement_percentage: Optional[Decimal]
    status: Optional[str]
    is_closed: bool


class IndicatorDashboard(BaseModel):
    indicator_name: str
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
    indicators: list


class TeamDashboardResponse(BaseModel):
    leader_id: UUID
    year: int
    team: list[UserDashboard]