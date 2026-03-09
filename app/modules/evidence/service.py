from sqlalchemy.orm import Session
from models import Evidence
from datetime import datetime


class EvidenceService:

    @staticmethod
    def create_evidence(db: Session, data, user_id):

        evidence = Evidence(
            indicator_tracking_id=data.indicator_tracking_id,
            file_path=data.file_path,
            uploaded_by=user_id,
            uploaded_at=datetime.utcnow()
        )

        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        return evidence

    @staticmethod
    def list_evidence(db: Session):

        return db.query(Evidence).all()