from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User
from app.models.indicator_assignment import IndicatorAssignment
from app.models.tracking import IndicatorTracking


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
            months.append({
                "month": t.month,
                "achieved_value": t.achieved_value,
                "achievement_percentage": t.achievement_percentage,
                "status": t.status,
                "is_closed": t.is_closed
            })

        result.append({
            "indicator_name": assignment.indicator_name,
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
            "indicators": user_dashboard["indicators"]
        })

    return {
        "leader_id": leader_id,
        "year": year,
        "team": result
    }