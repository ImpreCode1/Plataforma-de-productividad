import uuid
from sqlalchemy import Integer, Numeric, Boolean, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.models.base import Base


class IndicatorTracking(Base):
    __tablename__ = "indicator_tracking"

    __table_args__ = (
        UniqueConstraint("user_id", "position_indicator_id", "month"),
        Index("ix_tracking_user", "user_id"),
        Index("ix_tracking_position_indicator", "position_indicator_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    position_indicator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("position_indicators.id"),
        nullable=False
    )

    month: Mapped[int] = mapped_column(Integer, nullable=False)

    achieved_value: Mapped[float] = mapped_column(Numeric(12, 2))
    achievement_percentage: Mapped[float] = mapped_column(Numeric(5, 2))
    weighted_score: Mapped[float] = mapped_column(Numeric(6, 2))

    target_met: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship("User")
    position_indicator = relationship("PositionIndicator")
    action_plan = relationship("ActionPlan", back_populates="tracking", uselist=False)
    evidences = relationship("Evidence", back_populates="tracking")


class ActionPlan(Base):
    __tablename__ = "action_plans"
    __table_args__ = (
        UniqueConstraint("indicator_tracking_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    indicator_tracking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicator_tracking.id"),
        nullable=False
    )

    reason_not_met: Mapped[str] = mapped_column(String)
    action_plan: Mapped[str] = mapped_column(String)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    tracking = relationship("IndicatorTracking", back_populates="action_plan")


class Evidence(Base):
    __tablename__ = "evidences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    indicator_tracking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicator_tracking.id"),
        nullable=False
    )

    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    uploaded_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    tracking = relationship("IndicatorTracking", back_populates="evidences")