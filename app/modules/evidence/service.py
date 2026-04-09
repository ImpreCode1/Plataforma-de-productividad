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

def save_file(file: UploadFile) -> str:

    # Validar tipo
    allowed_types = ["application/pdf", "image/png", "image/jpeg"]

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Generar nombre único
    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"

    file_path = f"/uploads/evidences/{filename}"
    full_path = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with open(full_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path


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

    tracking = db.query(IndicatorTracking).filter(
        IndicatorTracking.id == evidence.tracking_id
    ).first()

    if tracking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")


# ------------------------------------------------
# CREATE EVIDENCE
# ------------------------------------------------

def create_evidence(db: Session, tracking_id, file: UploadFile, user_id):

    tracking = db.query(IndicatorTracking).filter(
        IndicatorTracking.id == tracking_id
    ).first()

    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")

    if tracking.is_closed:
        raise HTTPException(status_code=400, detail="Tracking is closed")

    if tracking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    file_path = save_file(file)

    evidence = Evidence(
        tracking_id=tracking_id,
        file_path=file_path,
        uploaded_by=user_id,
        uploaded_at=datetime.utcnow()
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


# ------------------------------------------------
# LIST EVIDENCE
# ------------------------------------------------

def list_evidence(db: Session, tracking_id):

    return db.query(Evidence).filter(
        Evidence.tracking_id == tracking_id
    ).all()


# ------------------------------------------------
# DELETE EVIDENCE
# ------------------------------------------------

def delete_evidence(db: Session, evidence_id):

    evidence = db.query(Evidence).filter(
        Evidence.id == evidence_id
    ).first()

    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    full_path = os.path.join(UPLOAD_DIR, evidence.file_path.split("/")[-1])
    if os.path.exists(full_path):
        os.remove(full_path)

    db.delete(evidence)
    db.commit()