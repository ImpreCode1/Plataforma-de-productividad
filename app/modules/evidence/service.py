import os
import uuid
from datetime import datetime
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.tracking import IndicatorTracking
from app.models.user import User


UPLOAD_DIR = "app/uploads/evidences"


# ------------------------------------------------
# SAVE FILE 🔥
# ------------------------------------------------

def save_file(file: UploadFile) -> tuple[str, str, int]:

    # Validar tipo
    allowed_types = ["application/pdf", "image/png", "image/jpeg"]

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Generar nombre único
    original_name = file.filename or "archivo"
    extension = original_name.split(".")[-1] if "." in original_name else "pdf"
    filename = f"{uuid.uuid4()}.{extension}"

    file_path = f"/uploads/evidences/{filename}"
    full_path = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file.file.seek(0)
    content = file.file.read()
    file_size = len(content)

    with open(full_path, "wb") as buffer:
        buffer.write(content)

    return file_path, original_name, file_size


# ------------------------------------------------
# CHECK ACCESS (LEADER can see team, ADMIN all, EMPLOYEE own)
# ------------------------------------------------

def check_access(db: Session, tracking_id, current_user):
    tracking = db.query(IndicatorTracking).filter(
        IndicatorTracking.id == tracking_id
    ).first()

    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")

    user_roles = [ur.role.name for ur in current_user.roles if ur.role]

    if "ADMIN" in user_roles:
        return

    if "LEADER" in user_roles:
        if tracking.user_id != current_user.id:
            team_member = db.query(User).filter(
                User.id == tracking.user_id,
                User.leader_id == current_user.id
            ).first()
            if not team_member:
                raise HTTPException(status_code=403, detail="Not authorized")
        return

    if tracking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")


# ------------------------------------------------
# CHECK EVIDENCE OWNERSHIP
# ------------------------------------------------

def check_evidence_ownership(db: Session, evidence_id, user_id):
    evidence = db.query(Evidence).filter(
        Evidence.id == evidence_id
    ).first()

    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    if evidence.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")


# ------------------------------------------------
# CREATE EVIDENCE (per tracking)
# ------------------------------------------------

def create_evidence_for_tracking(db: Session, file: UploadFile, tracking_id: str, current_user: User) -> Evidence:
    tracking = db.query(IndicatorTracking).filter(
        IndicatorTracking.id == tracking_id
    ).first()

    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking no encontrado")

    if tracking.approval_status == "APROBADO":
        raise HTTPException(status_code=400, detail="El KPI está aprobado, no se pueden subir más evidencias")

    user_roles = [ur.role.name for ur in current_user.roles if ur.role]
    is_owner = tracking.user_id == current_user.id
    is_leader = "LEADER" in user_roles and tracking.user and tracking.user.leader_id == current_user.id
    is_admin = "ADMIN" in user_roles

    if not (is_owner or is_leader or is_admin):
        raise HTTPException(status_code=403, detail="No autorizado para subir evidencias a este KPI")

    file_path, original_name, file_size = save_file(file)

    evidence = Evidence(
        tracking_id=tracking_id,
        user_id=tracking.user_id,
        year=tracking.year,
        month=tracking.month,
        file_path=file_path,
        original_filename=original_name,
        file_size=file_size,
        uploaded_by=current_user.id,
        uploaded_at=datetime.utcnow()
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


# ------------------------------------------------
# CREATE EVIDENCE (legacy, per month)
# ------------------------------------------------

def create_evidence(db: Session, file: UploadFile, user_id, tracking_id=None, year=None, month=None, target_user_id=None):

    file_path, original_name, file_size = save_file(file)

    if tracking_id:
        tracking = db.query(IndicatorTracking).filter(
            IndicatorTracking.id == tracking_id
        ).first()

        if not tracking:
            raise HTTPException(status_code=404, detail="Tracking not found")

        if tracking.is_closed:
            raise HTTPException(status_code=400, detail="Tracking is closed")

        if tracking.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        evidence = Evidence(
            tracking_id=tracking_id,
            file_path=file_path,
            original_filename=original_name,
            file_size=file_size,
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow()
        )

        db.add(evidence)
    else:
        if not year or not month:
            raise HTTPException(status_code=400, detail="year and month required")

        user_id_check = target_user_id or user_id

        evidence = Evidence(
            user_id=user_id_check,
            year=year,
            month=month,
            file_path=file_path,
            original_filename=original_name,
            file_size=file_size,
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow()
        )
        db.add(evidence)

    db.commit()
    db.refresh(evidence)
    return evidence


# ------------------------------------------------
# LIST EVIDENCE BY MONTH
# ------------------------------------------------

def list_evidences_by_month(db: Session, user_id, year, month):
    return db.query(Evidence).filter(
        Evidence.user_id == user_id,
        Evidence.year == year,
        Evidence.month == month
    ).all()


# ------------------------------------------------
# LIST EVIDENCE BY TRACKING
# ------------------------------------------------

def list_evidence(db: Session, tracking_id):

    return db.query(Evidence).filter(
        Evidence.tracking_id == tracking_id
    ).all()


# ------------------------------------------------
# DELETE EVIDENCE (only if tracking not approved)
# ------------------------------------------------

def delete_evidence(db: Session, evidence_id):

    evidence = db.query(Evidence).filter(
        Evidence.id == evidence_id
    ).first()

    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    if evidence.tracking_id:
        tracking = db.query(IndicatorTracking).filter(
            IndicatorTracking.id == evidence.tracking_id
        ).first()
        if tracking and tracking.approval_status == "APROBADO":
            raise HTTPException(status_code=400, detail="No se puede eliminar evidencia de un KPI aprobado")

    full_path = os.path.join(UPLOAD_DIR, evidence.file_path.split("/")[-1])
    if os.path.exists(full_path):
        os.remove(full_path)

    db.delete(evidence)
    db.commit()