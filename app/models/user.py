from sqlalchemy import Column, String, Boolean, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    external_auth_id = Column(String, nullable=True)
    document_number = Column(String, nullable=False, unique=True)

    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    position_name = Column(String, nullable=True)
    area = Column(String, nullable=True)
    subarea = Column(String, nullable=True)

    hire_date = Column(Date, nullable=True)
    contract_type = Column(String, nullable=True)
    salary_type = Column(String, nullable=True)

    leader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    is_active = Column(Boolean, default=True)

    # Relaciones
    leader = relationship("User", remote_side=[id], backref="subordinates")

    roles = relationship("UserRole", back_populates="user")
    assignments = relationship("IndicatorAssignment", back_populates="user")
    trackings = relationship("IndicatorTracking", back_populates="user")