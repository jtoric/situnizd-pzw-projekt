from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field


def _bcrypt_limit(value: str) -> str:
    # bcrypt uzima najviše 72 bajta; sve preko toga tiho ne bi ulazilo u hash
    if len(value.encode()) > 72:
        raise ValueError("Lozinka smije imati najviše 72 bajta")
    return value


Password = Annotated[str, Field(min_length=1), AfterValidator(_bcrypt_limit)]

# Lozinka koja se tek postavlja: uz isto ograničenje traži i najmanju duljinu
NewPassword = Annotated[str, Field(min_length=8), AfterValidator(_bcrypt_limit)]


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: Password


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
