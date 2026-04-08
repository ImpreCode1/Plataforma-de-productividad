from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.tracking import IndicatorTracking
from app.models.indicator_assignment import IndicatorAssignment
from app.models.action_plan import ActionPlan
from app.models.user import User


# ------------------------------------------------
# GET TEAM TRACKING (LEADER)
# ------------------------------------------------

def get_team_tracking(db: Session, leader_id: UUID, year: int):
    # Get subordinates
    team = db.query(User).filter(
        User.leader_id == leader_id,
        User.is_active == True
    ).all()

    team_user_ids = [u.id for u in team]

    # Get all tracking for team members
    trackings = db.query(IndicatorTracking).filter(
        IndicatorTracking.user_id.in_(team_user_ids),
        IndicatorTracking.year == year
    ).order_by(IndicatorTracking.user_id, IndicatorTracking.month).all()

    result = []
    for t in trackings:
        # Get user and assignment info
        user = db.query(User).filter(User.id == t.user_id).first()
        assignment = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.id == t.assignment_id
        ).first()

        # Get action plans
        action_plans = db.query(ActionPlan).filter(
            ActionPlan.tracking_id == t.id
        ).all()

        plans_data = []
        for plan in action_plans:
            plans_data.append({
                "id": str(plan.id),
                "reason_not_met": plan.reason_not_met,
                "action_plan": plan.action_plan,
                "created_at": plan.created_at.isoformat() if plan.created_at else None
            })

        result.append({
            "id": str(t.id),
            "user_id": str(t.user_id),
            "user_name": user.name if user else "Sin nombre",
            "user_email": user.email if user else "",
            "position_name": user.position_name if user else "",
            "assignment_id": str(t.assignment_id) if t.assignment_id else None,
            "indicator_name": assignment.indicator_name if assignment else "Sin indicador",
            "target_value": assignment.target_value if assignment else None,
            "weight": assignment.weight if assignment else None,
            "formula": assignment.formula if assignment else None,
            "year": t.year,
            "month": t.month,
            "achieved_value": float(t.achieved_value) if t.achieved_value else None,
            "achieved_total": float(t.achieved_total) if t.achieved_total else None,
            "achievement_percentage": float(t.achievement_percentage) if t.achievement_percentage else None,
            "weighted_score": float(t.weighted_score) if t.weighted_score else None,
            "target_met": t.target_met,
            "status": t.status,
            "is_closed": t.is_closed,
            "action_plans": plans_data
        })

    return result


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

    # Auto-crear plan de acción según resultado
    if tracking.target_met is True:
        # Meta cumplida - crear plan con mensaje satisfactorio
        plans = db.query(ActionPlan).filter(
            ActionPlan.tracking_id == tracking_id
        ).count()
        
        if plans == 0:
            action_plan = ActionPlan(
                tracking_id=tracking_id,
                reason_not_met="Meta cumplida",
                action_plan="Se alcanzó la meta establecida",
                created_by=tracking.user_id
            )
            db.add(action_plan)
    else:
        # Meta no cumplida - crear plan automático (líder debe editar después)
        plans = db.query(ActionPlan).filter(
            ActionPlan.tracking_id == tracking_id
        ).count()

        if plans == 0:
            action_plan = ActionPlan(
                tracking_id=tracking_id,
                reason_not_met="Cierre automático: meta no alcanzada",
                action_plan="Pendiente de definir - El líder debe completar el plan de acción",
                created_by=tracking.user_id
            )
            db.add(action_plan)

    tracking.is_closed = True
    tracking.status = "CLOSED"

    db.commit()
    db.refresh(tracking)

    return tracking