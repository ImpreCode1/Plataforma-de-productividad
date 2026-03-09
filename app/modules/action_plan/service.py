from uuid import UUID
from sqlalchemy.orm import Session
from app.models import ActionPlan
from datetime import datetime


class ActionPlanService:

    @staticmethod
    def create_plan(db: Session, data, user_id):

        plan = ActionPlan(
            indicator_tracking_id=data.indicator_tracking_id,
            reason_not_met=data.reason_not_met,
            action_plan=data.action_plan,
            created_by=user_id
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def list_plans(db: Session):

        return db.query(ActionPlan).all()

    @staticmethod
    def get_plan(db: Session, plan_id: UUID):

        return db.query(ActionPlan).filter(
            ActionPlan.id == plan_id
        ).first()

    @staticmethod
    def update_plan(db: Session, plan_id: UUID, data):

        plan = db.query(ActionPlan).filter(
            ActionPlan.id == plan_id
        ).first()

        if plan:
            plan.reason_not_met = data.reason_not_met
            plan.action_plan = data.action_plan
            db.commit()
            db.refresh(plan)

        return plan