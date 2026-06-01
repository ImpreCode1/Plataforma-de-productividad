from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base


class ApprovalConfig(Base):
    __tablename__ = "approval_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    config_type = Column(String, nullable=False)  # area | position | team | user
    config_value = Column(String, nullable=False)
    load_mode = Column(String, nullable=False)  # employee | leader | admin
    is_active = Column(Boolean, default=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", foreign_keys=[created_by], lazy="joined")
