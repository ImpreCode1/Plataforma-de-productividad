from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class PositionGroup(Base):
    __tablename__ = "position_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    level = Column(String, nullable=False)  # 'vicepresidencia' | 'direccion'

    parent_id = Column(UUID(as_uuid=True), ForeignKey("position_groups.id"), nullable=True)
    is_validated = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    parent = relationship("PositionGroup", remote_side=[id], backref="children")

    @property
    def full_path(self):
        """Ej: 'Financial Officer > Direccion Financiera (Mayreth Galvis)'"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
