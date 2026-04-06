from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base


class Evidence(Base):
    __tablename__ = "evidences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tracking_id = Column(UUID(as_uuid=True), ForeignKey("indicator_trackings.id"), nullable=False)
    file_path = Column(String, nullable=False)

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    tracking = relationship("IndicatorTracking", back_populates="evidences")