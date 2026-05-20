from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from app.models.user import User
from app.models.indicator_assignment import IndicatorAssignment
from app.models.tracking import IndicatorTracking
from app.models.action_plan import ActionPlan
from app.models.evidence import Evidence


def get_dashboard_by_user(db: Session, user_id: UUID, year: int, month: int = None):

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

        if trackings:
            for t in trackings:
                if month and t.month != month:
                    continue

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
                    "tracking_id": str(t.id),
                    "action_plans": plans_data,
                    "evidence_count": evidence_count
                })
        else:
            month_val = assignment.month
            
            if month and month_val != month:
                continue

            months.append({
                "month": month_val,
                "achieved_value": None,
                "achieved_total": None,
                "achievement_percentage": None,
                "status": "PENDING",
                "is_closed": False,
                "tracking_id": None,
                "action_plans": [],
                "evidence_count": 0
            })

        if month and not months:
            continue

        result.append({
            "id": str(assignment.id),
            "indicator_name": assignment.indicator_name,
            "formula": assignment.formula,
            "target_value": assignment.target_value,
            "weight": assignment.weight,
            "months": months
        })

    return {
        "user_id": user_id,
        "year": year,
        "month": month,
        "indicators": result
    }
    
def get_team_dashboard(db: Session, leader_id: UUID, year: int, month: int = None):

    # 1. Obtener subordinados
    team = db.query(User).filter(
        User.leader_id == leader_id,
        User.is_active == True
    ).all()

    result = []

    for user in team:

        # reutilizamos función existente 🔥
        user_dashboard = get_dashboard_by_user(db, user.id, year, month)

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
        "month": month,
        "team": result
    }


# ------------------------------------------------
# GLOBAL DASHBOARD (ADMIN) - All users overview
# ------------------------------------------------

def get_global_dashboard(db: Session, year: int, month: int = None, area: str = None):

    from app.modules.users.service import normalize_area

    all_users_query = db.query(User).filter(User.is_active == True)

    all_users = all_users_query.all()

    if area:
        normalized_area = normalize_area(area)
        if normalized_area:
            all_users = [
                u for u in all_users
                if normalize_area(u.area) == normalized_area
            ]

    filter_month = month

    total_users = len(all_users)
    total_indicators = 0
    total_tracked = 0
    total_closed = 0
    total_action_plans = 0
    total_evidence = 0

    monthly_stats = {m: {"total": 0, "closed": 0, "plans": 0, "evidence": 0, "score": 0} for m in range(1, 13)}

    team_summary = []

    for user in all_users:
        is_leader = db.query(User).filter(User.leader_id == user.id).count() > 0

        is_admin_role = any(
            ur.role.name == "ADMIN"
            for ur in user.roles if ur.role
        ) if user.roles else False

        is_leader_role = any(
            ur.role.name == "LEADER"
            for ur in user.roles if ur.role
        ) if user.roles else False

        all_assignments = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.user_id == user.id,
            IndicatorAssignment.year == year,
            IndicatorAssignment.is_active == True
        ).all()

        if filter_month:
            assignments = [a for a in all_assignments if a.month == filter_month]
        else:
            assignments = all_assignments
        
        user_indicators = len(assignments)

        total_indicators += user_indicators

        query = db.query(IndicatorTracking).filter(
            IndicatorTracking.user_id == user.id,
            IndicatorTracking.year == year
        )

        if filter_month:
            query = query.filter(IndicatorTracking.month == filter_month)

        trackings = query.all()

        tracked_count = len([t for t in trackings if t.status in ["COMPLETED", "CLOSED"]])
        closed_count = len([t for t in trackings if t.is_closed])
        total_tracked += tracked_count
        total_closed += closed_count

        user_plans = 0
        user_evidence = 0

        evidence_from_trackings = 0
        for t in trackings:
            plans = db.query(ActionPlan).filter(
                ActionPlan.tracking_id == t.id
            ).count()
            user_plans += plans

            evidence_from_trackings += db.query(Evidence).filter(
                Evidence.tracking_id == t.id
            ).count()

            if t.month in monthly_stats:
                monthly_stats[t.month]["total"] += 1
                if t.is_closed:
                    monthly_stats[t.month]["closed"] += 1
                monthly_stats[t.month]["plans"] += plans
                monthly_stats[t.month]["evidence"] += 1
                if t.weighted_score:
                    monthly_stats[t.month]["score"] += t.weighted_score

        evidence_without_tracking = db.query(Evidence).filter(
            Evidence.user_id == user.id,
            Evidence.year == year
        )
        if filter_month:
            evidence_without_tracking = evidence_without_tracking.filter(Evidence.month == filter_month)
        evidence_without_tracking = evidence_without_tracking.filter(Evidence.tracking_id == None).count()

        user_evidence = evidence_from_trackings + evidence_without_tracking

        total_action_plans += user_plans
        total_evidence += user_evidence

        if user.leader_id:
            leader = db.query(User).filter(User.id == user.leader_id).first()
            leader_name = leader.name if leader else "Sin líder"
        else:
            leader_name = "Sin líder"

        user_score = 0
        if trackings and assignments:
            indicator_groups = {}
            for assignment in assignments:
                indicator_name = assignment.indicator_name
                if indicator_name not in indicator_groups:
                    indicator_groups[indicator_name] = {
                        "weight": assignment.weight or 0,
                        "trackings": []
                    }
                trackings_ind = [t for t in trackings if t.assignment_id == assignment.id]
                if filter_month:
                    trackings_ind = [t for t in trackings_ind if t.month == filter_month]
                indicator_groups[indicator_name]["trackings"].extend(trackings_ind)
            
            for ind_name, ind_data in indicator_groups.items():
                trackings_with_data = [t for t in ind_data["trackings"] if t.achievement_percentage is not None]
                if trackings_with_data:
                    avg_achievement = sum(t.achievement_percentage for t in trackings_with_data) / len(trackings_with_data)
                    weighted = (avg_achievement * ind_data["weight"]) / 100
                    user_score += weighted

        indicators_by_name = {}
        for assignment in assignments:
            trackings_ind = [t for t in trackings if t.assignment_id == assignment.id]

            if trackings_ind:
                for t in trackings_ind:
                    if filter_month and t.month != filter_month:
                        continue

                    plans_count = db.query(ActionPlan).filter(ActionPlan.tracking_id == t.id).count()
                    evidence_count = db.query(Evidence).filter(
                        (Evidence.tracking_id == t.id) |
                        ((Evidence.tracking_id == None) & (Evidence.user_id == t.user_id) & (Evidence.year == t.year) & (Evidence.month == t.month))
                    ).count()

                    month_data = {
                        "month": t.month,
                        "is_closed": t.is_closed,
                        "achieved_value": float(t.achieved_value) if t.achieved_value else None,
                        "achieved_total": float(t.achieved_total) if t.achieved_total else None,
                        "achievement_percentage": float(t.achievement_percentage) if t.achievement_percentage else None,
                        "weighted_score": float(t.weighted_score) if t.weighted_score else None,
                        "target_met": t.target_met,
                        "plans_count": plans_count,
                        "evidence_count": evidence_count,
                        "has_action_plan": plans_count > 0,
                        "has_evidence": evidence_count > 0,
                    }

                    if assignment.indicator_name not in indicators_by_name:
                        indicators_by_name[assignment.indicator_name] = {
                            "indicator_name": assignment.indicator_name,
                            "weight": assignment.weight,
                            "target_value": assignment.target_value,
                            "months": []
                        }
                    indicators_by_name[assignment.indicator_name]["months"].append(month_data)
            else:
                if filter_month and assignment.month != filter_month:
                    continue

                month_data = {
                    "month": assignment.month,
                    "is_closed": False,
                    "achieved_value": None,
                    "achieved_total": None,
                    "achievement_percentage": None,
                    "weighted_score": None,
                    "target_met": None,
                    "plans_count": 0,
                    "evidence_count": 0,
                    "has_action_plan": False,
                    "has_evidence": False,
                }

                if assignment.indicator_name not in indicators_by_name:
                    indicators_by_name[assignment.indicator_name] = {
                        "indicator_name": assignment.indicator_name,
                        "weight": assignment.weight,
                        "target_value": assignment.target_value,
                        "months": []
                    }
                indicators_by_name[assignment.indicator_name]["months"].append(month_data)

        indicators_detail = list(indicators_by_name.values())

        team_summary.append({
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "position_name": user.position_name,
            "leader_name": leader_name,
            "indicators_count": user_indicators,
            "tracked_months": tracked_count,
            "closed_months": closed_count,
            "score": round(user_score, 2),
            "action_plans": user_plans,
            "evidence_count": user_evidence,
            "indicators": indicators_detail,
            "is_leader": is_leader,
            "is_leader_role": is_leader_role,
            "is_admin_role": is_admin_role
        })

    team_summary.sort(key=lambda x: x["score"], reverse=True)

    teams_data = {}
    for user in team_summary:
        leader = user["leader_name"]
        if leader not in teams_data:
            teams_data[leader] = {
                "leader_name": leader,
                "members": [],
                "total_indicators": 0,
                "total_closed": 0,
                "total_plans": 0,
                "total_evidence": 0,
                "total_score": 0
            }
        teams_data[leader]["members"].append(user)
        teams_data[leader]["total_indicators"] += user["indicators_count"]
        teams_data[leader]["total_closed"] += user["closed_months"]
        teams_data[leader]["total_plans"] += user["action_plans"]
        teams_data[leader]["total_evidence"] += user["evidence_count"]
        teams_data[leader]["total_score"] += user["score"]

    for team in teams_data.values():
        member_count = len(team["members"])
        team["avg_score"] = round(team["total_score"] / member_count, 2) if member_count > 0 else 0
        team["members"].sort(key=lambda x: x["score"], reverse=True)

    teams_list = sorted(teams_data.values(), key=lambda x: x["avg_score"], reverse=True)

    monthly_summary = []
    for m in range(1, 13):
        if monthly_stats[m]["total"] > 0:
            monthly_summary.append({
                "month": m,
                "total": monthly_stats[m]["total"],
                "closed": monthly_stats[m]["closed"],
                "plans": monthly_stats[m]["plans"],
                "evidence": monthly_stats[m]["evidence"],
                "avg_score": round(monthly_stats[m]["score"] / monthly_stats[m]["total"], 2) if monthly_stats[m]["total"] > 0 else 0
            })

    return {
        "year": year,
        "month": filter_month,
        "total_users": total_users,
        "total_indicators": total_indicators,
        "total_tracked": total_tracked,
        "total_closed": total_closed,
        "total_action_plans": total_action_plans,
        "total_evidence": total_evidence,
        "monthly_summary": monthly_summary,
        "teams": teams_list
    }