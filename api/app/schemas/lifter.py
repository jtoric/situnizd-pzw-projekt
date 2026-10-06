from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import reject_null


def _must_be_past(value: date | None) -> date | None:
    # Tip hvata pogrešan oblik, ali ne i besmislenu vrijednost
    if value is not None and value >= date.today():
        raise ValueError("Datum rođenja mora biti u prošlosti")
    return value


class LifterCreate(BaseModel):
    # Bez id, jer ga dodjeljuje baza, i bez club_id, jer je već u adresi rute
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    birth_date: date
    gender: Literal["M", "F"]

    @field_validator("birth_date")
    @classmethod
    def must_be_past(cls, v: date) -> date:
        return _must_be_past(v)


class LifterUpdate(BaseModel):
    # Sva polja neobavezna: PATCH šalje samo ono što se mijenja
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    birth_date: date | None = None
    gender: Literal["M", "F"] | None = None

    _not_null = field_validator(
        "first_name", "last_name", "birth_date", "gender", mode="before"
    )(reject_null)

    @field_validator("birth_date")
    @classmethod
    def must_be_past(cls, v: date | None) -> date | None:
        return _must_be_past(v)


class LifterResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: date
    gender: str
    club_id: int

    model_config = {"from_attributes": True}
