from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User
from app.models.indicator_assignment import IndicatorAssignment
from app.models.tracking import IndicatorTracking
from app.models.action_plan import ActionPlan
from app.models.evidence import Evidence


def get_dashboard_by_user(db: Session, user_id: UUID, year: int):

    assignments = db.query(IndicatorAssignment).filter(
        IndicatorAssignment.user_id == user_id,
        IndicatorAssignment.year == year,
        IndicatorAssignment.is_active == True
    ).all()

    result = []

    for assignment in assignments:

        trackings = db.query(IndicatorTracking).filter(
            IndicatorTracking.assignment_id == assignment.id
        ).order_by(IndicatorTracking.month).all()

        months = []

        for t in trackings:
            # Obtener planes de acción
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

            # Contar evidencias
            evidence_count = db.query(Evidence).filter(
                Evidence.tracking_id == t.id
            ).count()

            months.append({
                "month": t.month,
                "achieved_value": t.achieved_value,
                "achieved_total": t.achieved_total,
                "achievement_percentage": t.achievement_percentage,
                "status": t.status,
                "is_closed": t.is_closed,
                "tracking_id": t.id,
                "action_plans": plans_data,
                "evidence_count": evidence_count
            })

        result.append({
            "indicator_name": assignment.indicator_name,
            "formula": assignment.formula,
            "target_value": assignment.target_value,
            "weight": assignment.weight,
            "months": months
        })

    return {
        "user_id": user_id,
        "year": year,
        "indicators": result
    }
    
def get_team_dashboard(db: Session, leader_id: UUID, year: int):

    # 1. Obtener subordinados
    team = db.query(User).filter(
        User.leader_id == leader_id,
        User.is_active == True
    ).all()

    result = []

    for user in team:

        # reutilizamos función existente 🔥
        user_dashboard = get_dashboard_by_user(db, user.id, year)

        result.append({
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "position_name": user.position_name,
            "indicators": user_dashboard["indicators"]
        })

    return {
        "leader_id": leader_id,
        "year": year,
        "team": result
    }