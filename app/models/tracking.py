from sqlalchemy import Column, Integer, Numeric, Boolean, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base


class IndicatorTracking(Base):
    __tablename__ = "indicator_trackings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("indicator_assignments.id"), nullable=False)

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    achieved_value = Column(Numeric, nullable=True)
    achieved_total = Column(Numeric, nullable=True)  # Denominador (total)
    achievement_percentage = Column(Numeric, nullable=True)
    weighted_score = Column(Numeric, nullable=True)

    target_met = Column(Boolean, nullable=True)
    status = Column(String, nullable=True)

    is_closed = Column(Boolean, default=False)

    # === Nuevos campos de aprobación ===
    approval_status = Column(String, default="PENDIENTE")  # PENDIENTE | EN_REVISION | APROBADO | RECHAZADO
    submitted_at = Column(DateTime, nullable=True)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_comment = Column(Text, nullable=True)

    # Relaciones
    user = relationship("User", foreign_keys=[user_id], back_populates="trackings")
    assignment = relationship("IndicatorAssignment", back_populates="trackings")

    evidences = relationship("Evidence", back_populates="tracking", cascade="all, delete-orphan")
    action_plans = relationship("ActionPlan", back_populates="tracking", cascade="all, delete-orphan")

    approver = relationship("User", foreign_keys=[approved_by], lazy="joined")
    submitter = relationship("User", foreign_keys=[submitted_by], lazy="joined")