from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.tracking import IndicatorTracking
from app.models.indicator_assignment import IndicatorAssignment
from app.models.action_plan import ActionPlan


# ------------------------------------------------
# GET TRACKING BY USER + YEAR
# ------------------------------------------------

def get_tracking_by_user(db: Session, user_id: UUID, year: int):
    return db.query(IndicatorTracking).filter(
        IndicatorTracking.user_id == user_id,
        IndicatorTracking.year == year
    ).order_by(IndicatorTracking.month).all()


# ------------------------------------------------
# GET SINGLE TRACKING
# ------------------------------------------------

def get_tracking(db: Session, tracking_id: UUID):
    tracking = db.query(IndicatorTracking).filter(
        IndicatorTracking.id == tracking_id
    ).first()

    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")

    return tracking


# ------------------------------------------------
# UPDATE TRACKING (USER REPORTS)
# ------------------------------------------------

def update_tracking(db: Session, tracking_id: UUID, achieved_value):

    tracking = get_tracking(db, tracking_id)

    if tracking.is_closed:
        raise HTTPException(status_code=400, detail="Tracking is closed")

    assignment = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.id == tracking.assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # -----------------------------
    # CÁLCULOS 🔥
    # -----------------------------

    tracking.achieved_value = achieved_value

    if assignment.target_value > 0:
        achievement_percentage = (achieved_value / assignment.target_value) * 100
    else:
        achievement_percentage = 0

    weighted_score = (achievement_percentage * assignment.weight) / 100

    tracking.achievement_percentage = round(achievement_percentage, 2)
    tracking.weighted_score = round(weighted_score, 2)

    tracking.target_met = achieved_value >= assignment.target_value

    tracking.status = "COMPLETED"

    db.commit()
    db.refresh(tracking)

    return tracking


# ------------------------------------------------
# CLOSE TRACKING (LEADER)
# ------------------------------------------------

def close_tracking(db: Session, tracking_id: UUID):

    tracking = get_tracking(db, tracking_id)

    if tracking.is_closed:
        raise HTTPException(status_code=400, detail="Already closed")

    if tracking.achieved_value is None:
        raise HTTPException(status_code=400, detail="Cannot close without value")

    # 🔥 VALIDACIÓN CLAVE
    if tracking.target_met is False:
        plans = db.query(ActionPlan).filter(
            ActionPlan.tracking_id == tracking_id
        ).count()

        if plans == 0:
            raise HTTPException(
                status_code=400,
                detail="Action plan is required before closing"
            )

    tracking.is_closed = True
    tracking.status = "CLOSED"

    db.commit()
    db.refresh(tracking)

    return tracking