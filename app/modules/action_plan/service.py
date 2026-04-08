from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.action_plan import ActionPlan
from app.models.tracking import IndicatorTracking
from app.models.user import User


# ------------------------------------------------
# LIST TEAM ACTION PLANS (Leader's team)
# ------------------------------------------------

def list_team_action_plans(db: Session, leader_id: UUID, year: int):
    
    # 1. Get subordinates
    team = db.query(User).filter(
        User.leader_id == leader_id,
        User.is_active == True
    ).all()

    team_user_ids = [u.id for u in team]

    # 2. Get all tracking for those users in the year
    trackings = db.query(IndicatorTracking).filter(
        IndicatorTracking.user_id.in_(team_user_ids),
        IndicatorTracking.year == year,
        IndicatorTracking.is_closed == True
    ).all()

    # 3. Get action plans for each tracking
    result = []
    for tracking in trackings:
        action_plans = db.query(ActionPlan).filter(
            ActionPlan.tracking_id == tracking.id
        ).all()

        if action_plans:
            for plan in action_plans:
                # Get user info
                user = db.query(User).filter(User.id == tracking.user_id).first()
                
                # Get indicator info
                indicator_name = tracking.assignment.indicator_name if tracking.assignment else "Sin indicador"
                target_value = tracking.assignment.target_value if tracking.assignment else 0

                # Calculate achievement
                achieved_percentage = None
                if tracking.achieved_value and tracking.achieved_total:
                    achieved_percentage = (float(tracking.achieved_value) / float(tracking.achieved_total)) * 100

                result.append({
                    "id": str(plan.id),
                    "tracking_id": str(tracking.id),
                    "user_id": str(tracking.user_id),
                    "user_name": user.name if user else "Sin nombre",
                    "user_email": user.email if user else "",
                    "position_name": user.position_name if user else "",
                    "indicator_name": indicator_name,
                    "target_value": target_value,
                    "achieved_value": float(tracking.achieved_value) if tracking.achieved_value else None,
                    "achieved_total": float(tracking.achieved_total) if tracking.achieved_total else None,
                    "achieved_percentage": achieved_percentage,
                    "month": tracking.month,
                    "year": tracking.year,
                    "reason_not_met": plan.reason_not_met,
                    "action_plan": plan.action_plan,
                    "created_at": plan.created_at.isoformat() if plan.created_at else None
                })

    return result


# ------------------------------------------------
# CREATE
# ------------------------------------------------

def create_action_plan(db: Session, tracking_id: UUID, data, user_id):

    tracking = db.query(IndicatorTracking).filter(
        IndicatorTracking.id == tracking_id
    ).first()

    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")

    # Permitir crear plan de acción aunque esté cerrado (para que líder pueda completarlo)

    action_plan = ActionPlan(
        tracking_id=tracking_id,
        reason_not_met=data.reason_not_met,
        action_plan=data.action_plan,
        created_by=user_id
    )

    db.add(action_plan)
    db.commit()
    db.refresh(action_plan)

    return action_plan


# ------------------------------------------------
# LIST
# ------------------------------------------------

def list_action_plans(db: Session, tracking_id: UUID):

    return db.query(ActionPlan).filter(
        ActionPlan.tracking_id == tracking_id
    ).all()


# ------------------------------------------------
# UPDATE
# ------------------------------------------------

def update_action_plan(db: Session, action_plan_id: UUID, data):

    action_plan = db.query(ActionPlan).filter(
        ActionPlan.id == action_plan_id
    ).first()

    if not action_plan:
        raise HTTPException(status_code=404, detail="Action plan not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(action_plan, field, value)

    db.commit()
    db.refresh(action_plan)

    return action_plan