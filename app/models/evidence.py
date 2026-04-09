from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base


class Evidence(Base):
    __tablename__ = "evidences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tracking_id = Column(UUID(as_uuid=True), ForeignKey("indicator_trackings.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    year = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)

    file_path = Column(String, nullable=False)

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    tracking = relationship("IndicatorTracking", back_populates="evidences")