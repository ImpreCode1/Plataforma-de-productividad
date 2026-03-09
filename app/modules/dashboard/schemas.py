from uuid import UUID
from pydantic import BaseModel


class IndicatorDashboard(BaseModel):

    indicator_name: str
    target: float
    achieved: float
    achievement_percentage: float
    status: str
    
class UserIndicatorDashboard(BaseModel):

    indicator_id: UUID
    indicator_name: str

    target_value: float
    achieved_value: float

    achievement_percentage: float
    weighted_score: float

    status: str


class LeaderTeamIndicator(BaseModel):

    user_id: UUID
    user_name: str

    indicator_name: str

    achievement_percentage: float
    status: str


class OrganizationIndicatorSummary(BaseModel):

    indicator_name: str

    avg_achievement: float
    indicators_met: int
    indicators_not_met: int