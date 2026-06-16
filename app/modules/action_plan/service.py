import unicodedata
import re
import pandas as pd
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.action_plan import ActionPlan
from app.models.tracking import IndicatorTracking
from app.models.user import User
from app.models.indicator_assignment import IndicatorAssignment


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
                user = db.query(User).filter(User.id == tracking.user_id).first()
                
                indicator_name = tracking.assignment.indicator_name if tracking.assignment else "Sin indicador"
                target_value = tracking.assignment.target_value if tracking.assignment else 0

                achieved_percentage = None
                if tracking.achievement_percentage is not None:
                    achieved_percentage = float(tracking.achievement_percentage)
                elif tracking.achieved_value and tracking.achieved_total:
                    achieved_percentage = (float(tracking.achieved_value) / float(tracking.achieved_total)) * 100

                result.append({
                    "id": str(plan.id),
                    "tracking_id": str(tracking.id),
                    "user_id": str(tracking.user_id) if tracking.user_id else None,
                    "user_name": user.name if user and user.name else "Sin asignar",
                    "user_email": user.email if user and user.email else "",
                    "position_name": user.position_name if user and user.position_name else "",
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
# LIST MY ACTION PLANS (Employee)
# ------------------------------------------------

def list_my_action_plans(db: Session, user_id: UUID, year: int):
    
    trackings = db.query(IndicatorTracking).filter(
        IndicatorTracking.user_id == user_id,
        IndicatorTracking.year == year,
        IndicatorTracking.is_closed == True
    ).all()

    result = []
    for tracking in trackings:
        action_plans = db.query(ActionPlan).filter(
            ActionPlan.tracking_id == tracking.id
        ).all()

        if action_plans:
            for plan in action_plans:
                indicator_name = tracking.assignment.indicator_name if tracking.assignment else "Sin indicador"
                target_value = tracking.assignment.target_value if tracking.assignment else 0

                achieved_percentage = None
                if tracking.achievement_percentage is not None:
                    achieved_percentage = float(tracking.achievement_percentage)
                elif tracking.achieved_value and tracking.achieved_total:
                    achieved_percentage = (float(tracking.achieved_value) / float(tracking.achieved_total)) * 100

                result.append({
                    "id": str(plan.id),
                    "tracking_id": str(tracking.id),
                    "user_id": str(tracking.user_id) if tracking.user_id else None,
                    "user_name": "",
                    "position_name": "",
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


# ------------------------------------------------
# NORMALIZATION HELPERS
# ------------------------------------------------

def normalize_name(name):
    if not name:
        return name
    name = str(name)
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", name.strip()).lower()


def names_match(name1, name2, threshold=0.6):
    if not name1 or not name2:
        return False
    words1 = set(normalize_name(name1).lower().split())
    words2 = set(normalize_name(name2).lower().split())
    if not words1 or not words2:
        return False
    intersection = words1 & words2
    min_words = min(len(words1), len(words2))
    if min_words == 0:
        return False
    return len(intersection) / min_words >= threshold


def find_user_by_fuzzy_name(users_dict, target_name):
    if not target_name:
        return None
    target = normalize_name(target_name).lower()
    for key, user in users_dict.items():
        if isinstance(key, str) and names_match(key.lower(), target):
            return user
    return None


# ------------------------------------------------
# FUZZY INDICATOR MATCHER
# ------------------------------------------------

def find_indicator_by_fuzzy_name(assignments, target_name, threshold=0.5):
    if not target_name or not assignments:
        return None
    target = normalize_name(target_name)
    target_words = set(target.split())

    best = None
    best_score = 0

    for a in assignments:
        db_name = normalize_name(a.indicator_name)
        db_words = set(db_name.split())
        if not db_words:
            continue

        intersection = target_words & db_words
        score = len(intersection) / max(len(target_words), len(db_words), 1)

        if target in db_name or db_name in target:
            score = max(score, 0.85)

        if score > best_score:
            best_score = score
            best = a

    return best if best_score >= threshold else None


# ------------------------------------------------
# IMPORT ACTION PLANS FROM EXCEL
# ------------------------------------------------

def import_action_plans_from_excel(db: Session, file, year: int, month: int):
    df = pd.read_excel(file, header=None, skiprows=3, usecols=[0, 1, 2, 3])
    df.columns = ["Responsable", "Nombre del indicador", "reason_not_met", "action_plan"]

    created = 0
    updated = 0
    errors = []

    users_by_name = {}
    all_users = db.query(User).all()
    for user in all_users:
        normalized = normalize_name(user.name)
        users_by_name[normalized] = user

    for idx, row in df.iterrows():
        responsible_name = str(row.get("Responsable", "")).strip() if pd.notna(row.get("Responsable")) else ""
        indicator_name = str(row.get("Nombre del indicador", "")).strip().rstrip('.') if pd.notna(row.get("Nombre del indicador")) else ""
        reason = str(row.get("reason_not_met", "")).strip() if pd.notna(row.get("reason_not_met")) else ""
        action_plan = str(row.get("action_plan", "")).strip() if pd.notna(row.get("action_plan")) else ""

        if not indicator_name:
            errors.append({
                "fila": idx + 3,
                "responsable": responsible_name,
                "indicador": "",
                "motivo": "Nombre del indicador vacío"
            })
            continue

        if not action_plan:
            errors.append({
                "fila": idx + 3,
                "responsable": responsible_name,
                "indicador": indicator_name,
                "motivo": "Plan de acción vacío"
            })
            continue

        user = users_by_name.get(normalize_name(responsible_name))
        if not user:
            user = find_user_by_fuzzy_name(users_by_name, responsible_name)

        if not user:
            errors.append({
                "fila": idx + 3,
                "responsable": responsible_name,
                "indicador": indicator_name,
                "motivo": "Usuario no encontrado en la base de datos"
            })
            continue

        assignment = db.query(IndicatorAssignment).filter(
            IndicatorAssignment.user_id == user.id,
            IndicatorAssignment.year == year,
            IndicatorAssignment.month == month,
            IndicatorAssignment.indicator_name == indicator_name,
            IndicatorAssignment.is_active == True
        ).first()

        if not assignment:
            user_assignments = db.query(IndicatorAssignment).filter(
                IndicatorAssignment.user_id == user.id,
                IndicatorAssignment.year == year,
                IndicatorAssignment.month == month,
                IndicatorAssignment.is_active == True
            ).all()
            assignment = find_indicator_by_fuzzy_name(user_assignments, indicator_name)

        if not assignment:
            errors.append({
                "fila": idx + 3,
                "responsable": responsible_name,
                "indicador": indicator_name,
                "motivo": f"No se encontró el indicador asignado para {year}/{month}"
            })
            continue

        tracking = db.query(IndicatorTracking).filter(
            IndicatorTracking.assignment_id == assignment.id,
            IndicatorTracking.year == year,
            IndicatorTracking.month == month,
        ).first()

        if not tracking:
            tracking = IndicatorTracking(
                user_id=user.id,
                assignment_id=assignment.id,
                year=year,
                month=month,
                status="CLOSED",
                is_closed=True,
                approval_status="APROBADO",
            )
            db.add(tracking)
            db.flush()

        existing_plan = db.query(ActionPlan).filter(
            ActionPlan.tracking_id == tracking.id
        ).first()

        if existing_plan:
            existing_plan.reason_not_met = reason if reason else None
            existing_plan.action_plan = action_plan
            updated += 1
        else:
            plan = ActionPlan(
                tracking_id=tracking.id,
                reason_not_met=reason if reason else None,
                action_plan=action_plan,
                created_by=user.id,
            )
            db.add(plan)
            created += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "errors": errors,
    }

# ------------------------------------------------
# IMPORT ANNUAL ACTION PLANS FROM EXCEL (todos los meses en una hoja)
# ------------------------------------------------

MONTH_COLUMNS = {
    "Enero":      (2,  3,  1),
    "Febrero":    (4,  5,  2),
    "Marzo":      (6,  7,  3),
    "Abril":      (8,  9,  4),
    "Mayo":       (10, 11, 5),
    "Junio":      (12, 13, 6),
    "Julio":      (14, 15, 7),
    "Agosto":     (16, 17, 8),
    "Septiembre": (18, 19, 9),
    "Octubre":    (20, 21, 10),
    "Noviembre":  (22, 23, 11),
    "Diciembre":  (24, 25, 12),
}

def import_annual_action_plans_from_excel(db: Session, file, year: int):
    df = pd.read_excel(file, header=None, skiprows=3)

    created = 0
    updated = 0
    errors = []

    # Cargar todos los usuarios una sola vez
    users_by_name = {}
    for user in db.query(User).all():
        normalized = normalize_name(user.name)
        users_by_name[normalized] = user

    for idx, row in df.iterrows():
        responsible_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        indicator_name = str(row.iloc[1]).strip().rstrip('.') if pd.notna(row.iloc[1]) else ""

        if not responsible_name or not indicator_name:
            continue

        # Resolver usuario una vez por fila
        user = users_by_name.get(normalize_name(responsible_name))
        if not user:
            user = find_user_by_fuzzy_name(users_by_name, responsible_name)

        if not user:
            errors.append({
                "fila": idx + 4,
                "responsable": responsible_name,
                "indicador": indicator_name,
                "mes": "N/A",
                "motivo": "Usuario no encontrado en la base de datos"
            })
            continue

        # Iterar cada mes
        for month_name, (reason_col, plan_col, month_num) in MONTH_COLUMNS.items():
            reason = ""
            action_plan = ""

            if reason_col < len(row) and pd.notna(row.iloc[reason_col]):
                reason = str(row.iloc[reason_col]).strip()
            if plan_col < len(row) and pd.notna(row.iloc[plan_col]):
                action_plan = str(row.iloc[plan_col]).strip()

            # Si ambas celdas están vacías, saltar este mes
            if not reason and not action_plan:
                continue

            # Buscar assignment para este usuario/mes/año
            assignment = db.query(IndicatorAssignment).filter(
                IndicatorAssignment.user_id == user.id,
                IndicatorAssignment.year == year,
                IndicatorAssignment.month == month_num,
                IndicatorAssignment.indicator_name == indicator_name,
                IndicatorAssignment.is_active == True
            ).first()

            if not assignment:
                user_assignments = db.query(IndicatorAssignment).filter(
                    IndicatorAssignment.user_id == user.id,
                    IndicatorAssignment.year == year,
                    IndicatorAssignment.month == month_num,
                    IndicatorAssignment.is_active == True
                ).all()
                assignment = find_indicator_by_fuzzy_name(user_assignments, indicator_name)

            if not assignment:
                errors.append({
                    "fila": idx + 4,
                    "responsable": responsible_name,
                    "indicador": indicator_name,
                    "mes": month_name,
                    "motivo": f"Indicador no encontrado para {year}/{month_num}"
                })
                continue

            # Buscar o crear tracking
            tracking = db.query(IndicatorTracking).filter(
                IndicatorTracking.assignment_id == assignment.id,
                IndicatorTracking.year == year,
                IndicatorTracking.month == month_num,
            ).first()

            if not tracking:
                tracking = IndicatorTracking(
                    user_id=user.id,
                    assignment_id=assignment.id,
                    year=year,
                    month=month_num,
                    status="CLOSED",
                    is_closed=True,
                    approval_status="APROBADO",
                )
                db.add(tracking)
                db.flush()

            # Insertar o actualizar plan de acción
            existing_plan = db.query(ActionPlan).filter(
                ActionPlan.tracking_id == tracking.id
            ).first()

            if existing_plan:
                existing_plan.reason_not_met = reason if reason else None
                existing_plan.action_plan = action_plan if action_plan else existing_plan.action_plan
                updated += 1
            else:
                plan = ActionPlan(
                    tracking_id=tracking.id,
                    reason_not_met=reason if reason else None,
                    action_plan=action_plan,
                    created_by=user.id,
                )
                db.add(plan)
                created += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "errors": errors,
    }