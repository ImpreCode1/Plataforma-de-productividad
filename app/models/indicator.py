import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from decimal import Decimal

class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    formula_text: Mapped[str | None] = mapped_column(String(500))

    target_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )

    frequency: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # MONTHLY / QUARTERLY

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    position_links = relationship("PositionIndicator", back_populates="indicator")