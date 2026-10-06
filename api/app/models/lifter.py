from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.registration import Registration


class Lifter(Base):
    __tablename__ = "lifters"
    __table_args__ = (CheckConstraint("gender IN ('M', 'F')", name="ck_lifter_gender"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"), nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(1), nullable=False)

    registrations: Mapped[list["Registration"]] = relationship(back_populates="lifter")
