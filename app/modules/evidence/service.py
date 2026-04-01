from sqlalchemy.orm import Session
from app.models import Evidence
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status


class EvidenceService:

    @staticmethod
    def create_evidence(db: Session, data, user_id):

        evidence = Evidence(
            indicator_tracking_id=data.indicator_tracking_id,
            file_path=data.file_path,
            uploaded_by=user_id,
            status="pending"
        )

        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        return evidence

    @staticmethod
    def list_evidences(db: Session):

        return db.query(Evidence).all()

    @staticmethod
    def get_evidence(db: Session, evidence_id: UUID):

        return db.query(Evidence).filter(
            Evidence.id == evidence_id
        ).first()

    @staticmethod
    def list_user_evidences(db: Session, user_id: UUID):
        from app.models import IndicatorTracking
        return db.query(Evidence).join(
            IndicatorTracking
        ).filter(
            IndicatorTracking.user_id == user_id
        ).all()

    @staticmethod
    def list_team_evidences(db: Session, leader_id: UUID):
        from app.models import User, IndicatorTracking
        return db.query(Evidence).join(
            IndicatorTracking
        ).join(
            User, IndicatorTracking.user_id == User.id
        ).filter(
            User.leader_id == leader_id,
            Evidence.status == "pending"
        ).all()

    @staticmethod
    def review_evidence(db: Session, evidence_id: UUID, reviewer_id: UUID, status_review: str):
        
        evidence = db.query(Evidence).filter(
            Evidence.id == evidence_id
        ).first()

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidencia no encontrada"
            )

        if evidence.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_NOT_FOUND,
                detail="Evidencia ya ha sido revisada"
            )

        evidence.status = status_review
        evidence.reviewed_by = reviewer_id
        evidence.reviewed_at = datetime.utcnow()

        db.commit()
        db.refresh(evidence)

        return evidence

    @staticmethod
    def delete_evidence(db: Session, evidence_id: UUID):

        evidence = db.query(Evidence).filter(
            Evidence.id == evidence_id
        ).first()

        if evidence:
            db.delete(evidence)
            db.commit()

        return evidence