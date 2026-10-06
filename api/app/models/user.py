from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.club import Club


class User(Base):
    __tablename__ = "users"
    # Skup uloga provodi baza, pa ni upis iz konzole ne prolazi s ulogom "admn"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'club')", name="ck_user_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    # admin ne pripada nijednom klubu, pa je club_id NULL
    club_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("clubs.id"), nullable=True, index=True
    )
    club: Mapped[Optional["Club"]] = relationship(back_populates="users")
