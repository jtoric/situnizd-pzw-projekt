from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.competition import Competition
    from app.models.lifter import Lifter


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (
        # Isti natjecatelj najviše jednom po natjecanju; odjava ne briše redak,
        # pa ograničenje vrijedi i nakon nje
        UniqueConstraint(
            "lifter_id", "competition_id", name="uq_registration_lifter_competition"
        ),
        CheckConstraint("total >= 0", name="ck_registration_total"),
        CheckConstraint(
            "status IN ('active', 'withdrawn')", name="ck_registration_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lifter_id: Mapped[int] = mapped_column(
        ForeignKey("lifters.id"), nullable=False, index=True
    )
    competition_id: Mapped[int] = mapped_column(
        ForeignKey("competitions.id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
    # Vrijeme upisa daje baza, pa ne ovisi o satu poslužitelja
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    lifter: Mapped["Lifter"] = relationship(back_populates="registrations")
    competition: Mapped["Competition"] = relationship(back_populates="registrations")
