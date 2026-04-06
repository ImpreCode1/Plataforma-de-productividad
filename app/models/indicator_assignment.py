from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class IndicatorAssignment(Base):
    __tablename__ = "indicator_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    indicator_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)

    target_value = Column(Numeric, nullable=False)
    weight = Column(Numeric, nullable=False)

    is_active = Column(Boolean, default=True)

    # Relaciones
    user = relationship("User", back_populates="assignments")
    trackings = relationship("IndicatorTracking", back_populates="assignment")