import uuid
from datetime import date
from sqlalchemy import ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmploymentHistory(Base):
    __tablename__ = "employment_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    position_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("positions.id"),
        nullable=False
    )

    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user = relationship("User", backref="employment_history")
    position = relationship("Position")