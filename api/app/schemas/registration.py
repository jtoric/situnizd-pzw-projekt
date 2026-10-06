from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import reject_null

# Težinske kategorije IPF-a; nisu cijeli brojevi zbog otvorenih "120+" i "84+"
MALE_CATEGORIES = ["59", "66", "74", "83", "93", "105", "120", "120+"]
FEMALE_CATEGORIES = ["47", "52", "57", "63", "69", "76", "84", "84+"]
CATEGORIES_BY_GENDER = {"M": MALE_CATEGORIES, "F": FEMALE_CATEGORIES}


def _known_category(value: str | None) -> str | None:
    if value is not None and value not in MALE_CATEGORIES + FEMALE_CATEGORIES:
        raise ValueError(f"Nepoznata kategorija: {value}")
    return value


class RegistrationCreate(BaseModel):
    lifter_id: int
    category: str
    total: int = Field(default=0, ge=0)

    @field_validator("category")
    @classmethod
    def valid_category(cls, v: str) -> str:
        return _known_category(v)


class RegistrationUpdate(BaseModel):
    category: str | None = None
    total: int | None = Field(default=None, ge=0)

    _not_null = field_validator("category", "total", mode="before")(reject_null)

    @field_validator("category")
    @classmethod
    def valid_category(cls, v: str | None) -> str | None:
        return _known_category(v)


class LifterBrief(BaseModel):
    """Suženi natjecatelj unutar odgovora o prijavi: samo ono što popis treba."""

    first_name: str
    last_name: str

    model_config = {"from_attributes": True}


class RegistrationResponse(BaseModel):
    id: int
    lifter_id: int
    competition_id: int
    category: str
    total: int
    status: str
    registered_at: datetime
    lifter: LifterBrief

    model_config = {"from_attributes": True}
