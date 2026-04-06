from sqlalchemy import Column, Integer, Numeric, Boolean, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class IndicatorTracking(Base):
    __tablename__ = "indicator_trackings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("indicator_assignments.id"), nullable=False)

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    achieved_value = Column(Numeric, nullable=True)
    achievement_percentage = Column(Numeric, nullable=True)
    weighted_score = Column(Numeric, nullable=True)

    target_met = Column(Boolean, nullable=True)
    status = Column(String, nullable=True)

    is_closed = Column(Boolean, default=False)

    # Relaciones
    user = relationship("User", back_populates="trackings")
    assignment = relationship("IndicatorAssignment", back_populates="trackings")

    evidences = relationship("Evidence", back_populates="tracking", cascade="all, delete-orphan")
    action_plans = relationship("ActionPlan", back_populates="tracking", cascade="all, delete-orphan")