from pydantic import BaseModel, Field, field_validator

from app.schemas.auth import NewPassword
from app.schemas.common import reject_null


class ClubCreate(BaseModel):
    """Klub i, u istoj transakciji, račun kojim se klub prijavljuje."""

    name: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=80)
    username: str = Field(min_length=3, max_length=255)
    password: NewPassword


class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    city: str | None = Field(default=None, min_length=1, max_length=80)

    _not_null = field_validator("name", "city", mode="before")(reject_null)


class ClubResponse(BaseModel):
    id: int
    name: str
    city: str

    model_config = {"from_attributes": True}


class PasswordReset(BaseModel):
    new_password: NewPassword
