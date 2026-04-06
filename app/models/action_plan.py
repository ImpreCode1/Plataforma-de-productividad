from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base


class ActionPlan(Base):
    __tablename__ = "action_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tracking_id = Column(UUID(as_uuid=True), ForeignKey("indicator_trackings.id"), nullable=False)

    reason_not_met = Column(Text, nullable=True)
    action_plan = Column(Text, nullable=False)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    tracking = relationship("IndicatorTracking", back_populates="action_plans")