from sqlalchemy.orm import Session
from models import ActionPlan
from datetime import datetime


class ActionPlanService:

    @staticmethod
    def create_plan(db: Session, data, user_id):

        plan = ActionPlan(
            indicator_tracking_id=data.indicator_tracking_id,
            reason_not_met=data.reason_not_met,
            action_plan=data.action_plan,
            created_by=user_id,
            created_at=datetime.utcnow()
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def list_plans(db: Session):

        return db.query(ActionPlan).all()