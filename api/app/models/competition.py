import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.registration import Registration


class Competition(Base):
    __tablename__ = "competitions"
    __table_args__ = (
        CheckConstraint(
            "prelim_deadline < final_deadline", name="ck_competition_deadlines"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    # timestamptz: rok je trenutak na vremenskoj osi, neovisno o zoni čitatelja
    prelim_deadline: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    final_deadline: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    registrations: Mapped[list["Registration"]] = relationship(
        back_populates="competition"
    )
