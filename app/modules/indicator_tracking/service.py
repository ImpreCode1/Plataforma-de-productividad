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

def update_tracking(db: Session, tracking_id: UUID, achieved_value, achieved_total=None):

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
    tracking.achieved_total = achieved_total

    if achieved_total is not None and achieved_total > 0:
        achievement_percentage = (achieved_value / achieved_total) * 100
    elif assignment.target_value is not None and assignment.target_value > 0:
        achievement_percentage = (achieved_value / assignment.target_value) * 100
    else:
        achievement_percentage = 0

    weighted_score = (achievement_percentage * (assignment.weight or 0)) / 100

    tracking.achievement_percentage = round(achievement_percentage, 2)
    tracking.weighted_score = round(weighted_score, 2)

    target_met = False
    if achieved_total is not None and achieved_total > 0:
        target_met = achieved_value >= achieved_total
    elif assignment.target_value is not None:
        target_met = achieved_value >= assignment.target_value
    
    tracking.target_met = target_met

    tracking.status = "COMPLETED"

    db.commit()
    db.refresh(tracking)

    return tracking


# ------------------------------------------------
# CLOSE TRACKING (LEADER)
# ------------------------------------------------

def close_tracking(db: Session, tracking_id: UUID, achieved_value=None, achieved_total=None):

    tracking = get_tracking(db, tracking_id)

    if tracking.is_closed:
        raise HTTPException(status_code=400, detail="Already closed")

    # Allow leader to update value when closing
    if achieved_value is not None:
        tracking.achieved_value = achieved_value
        tracking.achieved_total = achieved_total
        
        assignment = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.id == tracking.assignment_id
        ).first()

        # Calcular: (logrado / total) * 100
        if achieved_total is not None and achieved_total > 0:
            achievement_percentage = (achieved_value / achieved_total) * 100
        elif assignment and assignment.target_value is not None and assignment.target_value > 0:
            achievement_percentage = (achieved_value / assignment.target_value) * 100
        else:
            achievement_percentage = 0

        weighted_score = (achievement_percentage * (assignment.weight if assignment else 0)) / 100

        tracking.achievement_percentage = round(achievement_percentage, 2)
        tracking.weighted_score = round(weighted_score, 2)
        
        # Comparar logrado vs total
        target_met = False
        if achieved_total is not None and achieved_total > 0:
            target_met = achieved_value >= achieved_total
        elif assignment and assignment.target_value is not None:
            target_met = achieved_value >= assignment.target_value
        
        tracking.target_met = target_met
        tracking.status = "COMPLETED"

    elif tracking.achieved_value is None:
        raise HTTPException(status_code=400, detail="Cannot close without value")

    # 🔥 VALIDACIÓN CLAVE - Auto-crear plan de acción si no existe
    if tracking.target_met is False:
        plans = db.query(ActionPlan).filter(
            ActionPlan.tracking_id == tracking_id
        ).count()

        if plans == 0:
            from app.models import User
            action_plan = ActionPlan(
                tracking_id=tracking_id,
                reason_not_met="Cierre automático: meta no alcanzada",
                action_plan="Pendiente de definir",
                created_by=tracking.user_id
            )
            db.add(action_plan)

    tracking.is_closed = True
    tracking.status = "CLOSED"

    db.commit()
    db.refresh(tracking)

    return tracking