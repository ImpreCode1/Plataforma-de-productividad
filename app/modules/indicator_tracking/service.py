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
            "approval_status": t.approval_status,
            "submitted_at": t.submitted_at.isoformat() if t.submitted_at else None,
            "submitted_by": str(t.submitted_by) if t.submitted_by else None,
            "approved_by": str(t.approved_by) if t.approved_by else None,
            "approved_at": t.approved_at.isoformat() if t.approved_at else None,
            "rejection_comment": t.rejection_comment,
            "action_plans": plans_data
        })

    return result


# ------------------------------------------------
# GET TRACKING BY USER + YEAR
# ------------------------------------------------

def get_tracking_by_user(db: Session, user_id: UUID, year: int):
    from sqlalchemy.orm import joinedload
    from app.models.evidence import Evidence
    from app.models.indicator_assignment import IndicatorAssignment
    
    trackings = db.query(IndicatorTracking).options(
        joinedload(IndicatorTracking.evidences),
        joinedload(IndicatorTracking.assignment)
    ).filter(
        IndicatorTracking.user_id == user_id,
        IndicatorTracking.year == year
    ).order_by(IndicatorTracking.month).all()
    
    for t in trackings:
        t.evidence_count = len(t.evidences) if t.evidences else 0
        t.evidences = t.evidences or []
        if t.assignment:
            t.indicator_name = t.assignment.indicator_name
            t.target_value = t.assignment.target_value
            t.weight = t.assignment.weight
            t.formula = t.assignment.formula
    
    return trackings


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

    if tracking.approval_status == "APROBADO":
        raise HTTPException(status_code=400, detail="El KPI está aprobado y no puede editarse")

    if tracking.is_closed and tracking.approval_status != "RECHAZADO":
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

    if tracking.approval_status == "RECHAZADO":
        tracking.approval_status = "PENDIENTE"
        tracking.rejection_comment = None

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
        
        # Comparar achievement_percentage vs target_value (meta del indicador)
        target_met = False
        if assignment and assignment.target_value is not None:
            target_met = achievement_percentage >= assignment.target_value
        elif achieved_total is not None and achieved_total > 0:
            target_met = (achieved_value / achieved_total * 100) >= 100
        
        tracking.target_met = target_met
        tracking.status = "COMPLETED"

    elif tracking.achieved_value is None:
        raise HTTPException(status_code=400, detail="Cannot close without value")

    tracking.is_closed = True
    tracking.status = "CLOSED"
    tracking.approval_status = "APROBADO"

    db.commit()
    db.refresh(tracking)

    return tracking


# ------------------------------------------------
# CLOSE ASSIGNMENT DIRECTLY (NEW MODEL)
# ------------------------------------------------

def close_assignment_direct(db: Session, assignment_id: UUID, achieved_value=None, achieved_total=None, user_id: UUID = None):
    assignment = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if not assignment.is_active:
        raise HTTPException(status_code=400, detail="Assignment is not active")

    tracking = db.query(IndicatorTracking).filter(
        IndicatorTracking.assignment_id == assignment_id
    ).first()

    if tracking:
        if tracking.is_closed:
            raise HTTPException(status_code=400, detail="Already closed")
    else:
        tracking = IndicatorTracking(
            user_id=assignment.user_id,
            assignment_id=assignment_id,
            year=assignment.year,
            month=assignment.month,
            status="PENDING",
            is_closed=False
        )
        db.add(tracking)
        db.flush()

    if achieved_value is not None:
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
        if assignment.target_value is not None:
            target_met = achievement_percentage >= assignment.target_value
        
        tracking.target_met = target_met
        tracking.status = "COMPLETED"

    tracking.is_closed = True
    tracking.approval_status = "APROBADO"

    db.commit()
    db.refresh(tracking)

    return tracking