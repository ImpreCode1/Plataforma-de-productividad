from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import IndicatorTracking, PositionIndicator, Indicator

class DashboardService:

    @staticmethod   
    def user_dashboard(db: Session, user_id, month):
        results = (
            db.query(
                Indicator.id,
                Indicator.name,
                PositionIndicator.target_value,
                IndicatorTracking.achieved_value,
                IndicatorTracking.achievement_percentage,
                IndicatorTracking.weighted_score,
                IndicatorTracking.status,
                IndicatorTracking.target_met
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

        if not results:
            return {
                "general_compliance": 0,
                "total_indicators": 0,
                "pending": 0,
                "by_indicator": []
            }

        total_indicators = len(results)
        total_weighted_score = sum(float(r.weighted_score or 0) for r in results)
        pending = sum(1 for r in results if r.achieved_value is None)
        
        general_compliance = round(total_weighted_score / total_indicators, 1) if total_indicators > 0 else 0

        by_indicator = []
        for r in results:
            compliance = float(r.achievement_percentage or 0)
            by_indicator.append({
                "name": r.name,
                "compliance": compliance,
                "status": "green" if compliance >= 100 else "yellow" if compliance >= 80 else "red"
            })

        return {
            "general_compliance": general_compliance,
            "total_indicators": total_indicators,
            "pending": pending,
            "by_indicator": by_indicator
        }
    
    @staticmethod
    def leader_dashboard(db: Session, leader_id, month):
        results = (
            db.query(
                Indicator.name,
                func.avg(IndicatorTracking.achievement_percentage).label("avg_achievement"),
                func.count(IndicatorTracking.id).label("count"),
                func.sum(func.case((IndicatorTracking.target_met == True, 1), else_=0)).label("met")
            )
            .join(
                PositionIndicator,
                IndicatorTracking.position_indicator_id == PositionIndicator.id
            )
            .join(
                Indicator,
                PositionIndicator.indicator_id == Indicator.id
            )
            .join(
                "user",
                IndicatorTracking.user_id == "user.id"
            )
            .filter(
                "user.leader_id" == str(leader_id)
            )
            .filter(
                IndicatorTracking.month == month
            )
            .group_by(Indicator.name)
            .all()
        )

        return [
            {
                "indicator": r.name,
                "avg_achievement": float(r.avg_achievement or 0),
                "count": r.count,
                "met": r.met
            }
            for r in results
        ]
    
    @staticmethod
    def organization_dashboard(db: Session, month):
        results = (
            db.query(
                Indicator.name,
                func.avg(IndicatorTracking.achievement_percentage).label("avg_achievement"),
                func.sum(func.case((IndicatorTracking.target_met == True, 1), else_=0)).label("met"),
                func.sum(func.case((IndicatorTracking.target_met == False, 1), else_=0)).label("not_met")
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
            .group_by(Indicator.name)
            .all()
        )

        return [
            {
                "indicator": r.name,
                "avg_achievement": float(r.avg_achievement or 0),
                "met": r.met,
                "not_met": r.not_met
            }
            for r in results
        ]