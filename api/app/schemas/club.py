from pydantic import BaseModel, Field

from app.schemas.auth import NewPassword


class ClubCreate(BaseModel):
    """Klub i, u istoj transakciji, račun kojim se klub prijavljuje."""

    name: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=80)
    username: str = Field(min_length=3, max_length=255)
    password: NewPassword


class ClubUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    city: str | None = Field(default=None, min_length=1, max_length=80)


class ClubResponse(BaseModel):
    id: int
    name: str
    city: str

    model_config = {"from_attributes": True}


class PasswordReset(BaseModel):
    new_password: NewPassword
