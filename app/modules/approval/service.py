from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from datetime import datetime

from app.models.tracking import IndicatorTracking
from app.models.indicator_assignment import IndicatorAssignment
from app.models.user import User
from app.models.action_plan import ActionPlan
from app.modules.notifications import service as notification_service
from app.modules.evidence.service import _ensure_tracking_for_assignment


def _get_tracking_or_404(db: Session, tracking_id: UUID) -> IndicatorTracking:
    tracking = db.query(IndicatorTracking).filter(IndicatorTracking.id == tracking_id).first()
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking no encontrado")
    return tracking


def _get_assignment_or_404(db: Session, assignment_id: UUID) -> IndicatorAssignment:
    assignment = db.query(IndicatorAssignment).filter(IndicatorAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return assignment


def _is_leader_of(user: User, target_user_id: UUID, db: Session) -> bool:
    if user.id == target_user_id:
        return True
    target = db.query(User).filter(User.id == target_user_id).first()
    if not target:
        return False
    return target.leader_id == user.id


def _can_approve(user: User, tracking: IndicatorTracking, db: Session) -> bool:
    user_roles = [ur.role.name for ur in user.roles if ur.role]
    if "ADMIN" in user_roles:
        return True
    if "LEADER" in user_roles:
        return _is_leader_of(user, tracking.user_id, db)
    return False


def _save_action_plan(db: Session, tracking_id: UUID, reason_not_met: str | None, action_plan: str | None, current_user: User):
    if not action_plan and not reason_not_met:
        return

    existing = db.query(ActionPlan).filter(
        ActionPlan.tracking_id == tracking_id
    ).first()

    if existing:
        if action_plan is not None:
            existing.action_plan = action_plan
        if reason_not_met is not None:
            existing.reason_not_met = reason_not_met
    else:
        plan = ActionPlan(
            tracking_id=tracking_id,
            reason_not_met=reason_not_met or "",
            action_plan=action_plan or "",
            created_by=current_user.id,
            created_at=datetime.utcnow(),
        )
        db.add(plan)

    db.flush()


def submit_assignment(db: Session, assignment_id: UUID, current_user: User, reason_not_met: str | None = None, action_plan: str | None = None) -> IndicatorTracking:
    assignment = _get_assignment_or_404(db, assignment_id)

    if not assignment.is_active:
        raise HTTPException(status_code=400, detail="La asignación está cerrada")

    if assignment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el colaborador asignado puede enviar este KPI")

    tracking = _ensure_tracking_for_assignment(db, assignment_id)

    if tracking.approval_status == "APROBADO":
        raise HTTPException(status_code=400, detail="El KPI ya está aprobado y no puede modificarse")

    if tracking.approval_status == "EN_REVISION":
        raise HTTPException(status_code=400, detail="El KPI ya está en revisión")

    if tracking.achieved_value is None:
        raise HTTPException(status_code=400, detail="Debes registrar un valor antes de enviar a revisión")

    _save_action_plan(db, tracking.id, reason_not_met, action_plan, current_user)

    tracking.approval_status = "EN_REVISION"
    tracking.submitted_at = datetime.utcnow()
    tracking.submitted_by = current_user.id
    tracking.status = "COMPLETED"

    db.commit()
    db.refresh(tracking)

    try:
        notification_service.notify_leader_submitted(db, tracking, current_user)
    except Exception:
        pass

    return tracking


def submit_tracking(db: Session, tracking_id: UUID, current_user: User, reason_not_met: str | None = None, action_plan: str | None = None) -> IndicatorTracking:
    tracking = _get_tracking_or_404(db, tracking_id)

    if tracking.approval_status == "APROBADO":
        raise HTTPException(status_code=400, detail="El KPI ya está aprobado y no puede modificarse")

    if tracking.approval_status == "EN_REVISION":
        raise HTTPException(status_code=400, detail="El KPI ya está en revisión")

    if tracking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el colaborador asignado puede enviar este KPI")

    if tracking.achieved_value is None:
        raise HTTPException(status_code=400, detail="Debes registrar un valor antes de enviar a revisión")

    _save_action_plan(db, tracking.id, reason_not_met, action_plan, current_user)

    tracking.approval_status = "EN_REVISION"
    tracking.submitted_at = datetime.utcnow()
    tracking.submitted_by = current_user.id
    tracking.status = "COMPLETED"

    db.commit()
    db.refresh(tracking)

    try:
        notification_service.notify_leader_submitted(db, tracking, current_user)
    except Exception:
        pass

    return tracking


def approve_tracking(db: Session, tracking_id: UUID, current_user: User) -> IndicatorTracking:
    tracking = _get_tracking_or_404(db, tracking_id)

    if not _can_approve(current_user, tracking, db):
        raise HTTPException(status_code=403, detail="No tienes permisos para aprobar este KPI")

    if tracking.approval_status != "EN_REVISION":
        raise HTTPException(status_code=400, detail="El KPI debe estar en revisión para ser aprobado")

    tracking.approval_status = "APROBADO"
    tracking.approved_by = current_user.id
    tracking.approved_at = datetime.utcnow()
    tracking.is_closed = True
    tracking.status = "CLOSED"

    db.commit()
    db.refresh(tracking)

    try:
        notification_service.notify_employee_approved(db, tracking, current_user)
    except Exception:
        pass

    return tracking


def reject_tracking(db: Session, tracking_id: UUID, current_user: User, comment: str) -> IndicatorTracking:
    tracking = _get_tracking_or_404(db, tracking_id)

    if not _can_approve(current_user, tracking, db):
        raise HTTPException(status_code=403, detail="No tienes permisos para rechazar este KPI")

    if tracking.approval_status != "EN_REVISION":
        raise HTTPException(status_code=400, detail="El KPI debe estar en revisión para ser rechazado")

    if not comment or not comment.strip():
        raise HTTPException(status_code=400, detail="El comentario de rechazo es obligatorio")

    tracking.approval_status = "RECHAZADO"
    tracking.rejection_comment = comment.strip()
    tracking.approved_by = current_user.id
    tracking.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(tracking)

    try:
        notification_service.notify_employee_rejected(db, tracking, current_user, comment.strip())
    except Exception:
        pass

    return tracking
