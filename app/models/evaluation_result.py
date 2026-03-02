import uuid
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False
    )

    indicator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicators.id"),
        nullable=False
    )

    achieved_value: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    achievement_percentage: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )

    weighted_score: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False
    )

    evaluation = relationship("Evaluation", back_populates="results")
    indicator = relationship("Indicator")
    evidences = relationship("Evidence", back_populates="evaluation_result")
    action_plan = relationship("ActionPlan", back_populates="evaluation_result", uselist=False)