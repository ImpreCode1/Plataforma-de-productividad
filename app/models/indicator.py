import uuid
from sqlalchemy import String, Boolean, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.models.base import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    formula_text: Mapped[str] = mapped_column(String, nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class PositionIndicator(Base):
    __tablename__ = "position_indicators"
    __table_args__ = (
        UniqueConstraint("position_id", "indicator_id", "year"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    position_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("positions.id"),
        nullable=False
    )

    indicator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicators.id"),
        nullable=False
    )

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    target_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    position = relationship("Position")
    indicator = relationship("Indicator")