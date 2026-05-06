from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class IndicatorAssignment(Base):
    __tablename__ = "indicator_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    indicator_name = Column(String, nullable=False)
    formula = Column(Text, nullable=True)
    year = Column(Integer, nullable=False)

    target_value = Column(Numeric, nullable=False)
    weight = Column(Numeric, nullable=False)
    frequency = Column(String, default="MONTHLY")

    is_active = Column(Boolean, default=True)

    start_month = Column(Integer, default=1)
    end_month = Column(Integer, default=12)

    position_name_at_assignment = Column(String, nullable=True)
    area_at_assignment = Column(String, nullable=True)
    subarea_at_assignment = Column(String, nullable=True)
    direccion_at_assignment = Column(String, nullable=True)
    linea_at_assignment = Column(String, nullable=True)
    numero_linea_at_assignment = Column(String, nullable=True)

    # Relaciones
    user = relationship("User", back_populates="assignments")
    trackings = relationship("IndicatorTracking", back_populates="assignment")