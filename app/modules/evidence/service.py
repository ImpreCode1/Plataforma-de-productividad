from sqlalchemy.orm import Session
from app.models import Evidence
from datetime import datetime
from uuid import UUID


class EvidenceService:

    @staticmethod
    def create_evidence(db: Session, data, user_id):

        evidence = Evidence(
            indicator_tracking_id=data.indicator_tracking_id,
            file_path=data.file_path,
            uploaded_by=user_id
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
    def delete_evidence(db: Session, evidence_id: UUID):

        evidence = db.query(Evidence).filter(
            Evidence.id == evidence_id
        ).first()

        if evidence:
            db.delete(evidence)
            db.commit()

        return evidence