from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.action_plan import ActionPlan
from app.models.tracking import IndicatorTracking


# ------------------------------------------------
# CREATE
# ------------------------------------------------

def create_action_plan(db: Session, tracking_id: UUID, data, user_id):

    tracking = db.query(IndicatorTracking).filter(
        IndicatorTracking.id == tracking_id
    ).first()

    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")

    if tracking.is_closed:
        raise HTTPException(status_code=400, detail="Tracking is closed")

    if tracking.target_met:
        raise HTTPException(
            status_code=400,
            detail="Action plan not required (target met)"
        )

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