from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)

    users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")