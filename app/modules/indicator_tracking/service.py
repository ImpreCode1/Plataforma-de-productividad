from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.models import IndicatorTracking, PositionIndicator
from datetime import datetime


class IndicatorTrackingService:

    @staticmethod
    def create_tracking(db: Session, data):

        position_indicator = db.query(PositionIndicator).filter(
            PositionIndicator.id == data.position_indicator_id
        ).first()

        if not position_indicator:
            raise HTTPException(
                status_code=404,
                detail="Position Indicator not found"
            )

        target = float(position_indicator.target_value)
        weight = float(position_indicator.weight)

        achievement_percentage = (data.achieved_value / target) * 100

        weighted_score = (achievement_percentage * weight) / 100

        target_met = achievement_percentage >= 100

        status = "met" if target_met else "not_met"

        tracking = IndicatorTracking(
            user_id=data.user_id,
            position_indicator_id=data.position_indicator_id,
            month=data.month,
            achieved_value=data.achieved_value,
            achievement_percentage=achievement_percentage,
            weighted_score=weighted_score,
            target_met=target_met,
            status=status,
            created_at=datetime.now()
        )

        db.add(tracking)
        db.commit()
        db.refresh(tracking)

        return tracking

    @staticmethod
    def get_tracking(db: Session, tracking_id: UUID):

        return db.query(IndicatorTracking).filter(
            IndicatorTracking.id == tracking_id
        ).first()

    @staticmethod
    def list_tracking(
        db,
        user_id=None,
        month=None,
        year=None,
        position_indicator_id=None
    ):

        query = db.query(IndicatorTracking)

        if user_id:
            query = query.filter(IndicatorTracking.user_id == user_id)

        if month:
            query = query.filter(IndicatorTracking.month == month)

        if position_indicator_id:
            query = query.filter(
                IndicatorTracking.position_indicator_id == position_indicator_id
            )

        if year:
            query = query.join(
                PositionIndicator,
                IndicatorTracking.position_indicator_id == PositionIndicator.id
            ).filter(PositionIndicator.year == year)

        return query.all()

    @staticmethod
    def update_tracking(db: Session, tracking_id: UUID, achieved_value: float):

        tracking = db.query(IndicatorTracking).filter(
            IndicatorTracking.id == tracking_id
        ).first()

        if not tracking:
            raise HTTPException(
                status_code=404,
                detail="Indicator tracking not found"
            )

        position_indicator = db.query(PositionIndicator).filter(
            PositionIndicator.id == tracking.position_indicator_id
        ).first()

        if not position_indicator:
            raise HTTPException(
                status_code=404,
                detail="Position indicator not found"
            )

        target = float(position_indicator.target_value)
        weight = float(position_indicator.weight)

        achievement_percentage = (achieved_value / target) * 100
        weighted_score = (achievement_percentage * weight) / 100

        target_met = achievement_percentage >= 100
        status = "met" if target_met else "not_met"

        tracking.achieved_value = achieved_value
        tracking.achievement_percentage = achievement_percentage
        tracking.weighted_score = weighted_score
        tracking.target_met = target_met
        tracking.status = status

        db.commit()
        db.refresh(tracking)

        return tracking