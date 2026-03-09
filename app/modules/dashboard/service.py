from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import IndicatorTracking, PositionIndicator, Indicator
from app.models.user import User

class DashboardService:

    @staticmethod   
    def user_dashboard(
        db: Session,
        user_id,
        month
    ):

        results = (
            db.query(
                Indicator.id,
                Indicator.name,
                PositionIndicator.target_value,
                IndicatorTracking.achieved_value,
                IndicatorTracking.achievement_percentage,
                IndicatorTracking.weighted_score,
                IndicatorTracking.status
            )

            .join(
                PositionIndicator,
                IndicatorTracking.position_indicator_id == PositionIndicator.id
            )

            .join(
                Indicator,
                PositionIndicator.indicator_id == Indicator.id
            )

            .filter(
                IndicatorTracking.user_id == user_id
            )

            .filter(
                IndicatorTracking.month == month
            )

            .all()
        )

        return results
    
    @staticmethod
    def leader_dashboard(
        db: Session,
        leader_id,
        month
    ):

        results = (
            db.query(
                User.id,
                User.name,
                Indicator.name,
                IndicatorTracking.achievement_percentage,
                IndicatorTracking.status
            )

            .join(
                IndicatorTracking,
                IndicatorTracking.user_id == User.id
            )

            .join(
                PositionIndicator,
                IndicatorTracking.position_indicator_id == PositionIndicator.id
            )

            .join(
                Indicator,
                PositionIndicator.indicator_id == Indicator.id
            )

            .filter(
                User.leader_id == leader_id
            )

            .filter(
                IndicatorTracking.month == month
            )

            .all()
        )

        return results
    
    @staticmethod
    def organization_dashboard(
        db: Session,
        month
    ):

        results = (
            db.query(
                Indicator.name,

                func.avg(
                    IndicatorTracking.achievement_percentage
                ).label("avg_achievement"),

                func.sum(
                    func.case(
                        (IndicatorTracking.target_met == True, 1),
                        else_=0
                    )
                ).label("indicators_met"),

                func.sum(
                    func.case(
                        (IndicatorTracking.target_met == False, 1),
                        else_=0
                    )
                ).label("indicators_not_met")
            )

            .join(
                PositionIndicator,
                IndicatorTracking.position_indicator_id == PositionIndicator.id
            )

            .join(
                Indicator,
                PositionIndicator.indicator_id == Indicator.id
            )

            .filter(
                IndicatorTracking.month == month
            )

            .group_by(
                Indicator.name
            )

            .all()
        )

        return results