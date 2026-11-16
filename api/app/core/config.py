from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env stoji u korijenu repozitorija: api/app/core/config.py -> parents[3]
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

# Ključevi koji su javni, jer stoje u kodu ili u .env.example; vrijede samo u razvoju
PUBLIC_SECRETS = {"change-me", "dev-only-secret-change-me-in-production-0123456789"}


class Settings(BaseSettings):
    APP_NAME: str = "Powerlifting Registrations API"
    ENV: str = "dev"
    DATABASE_URL: str
    JWT_SECRET: str = "change-me"
    JWT_ISSUER: str = "sit-unizd"

    # Varijabla okoline ima prednost pred vrijednošću iz .env datoteke
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    @model_validator(mode="after")
    def secret_is_private_outside_dev(self):
        # Tko zna ključ, potpisuje vlastite tokene s bilo kojom ulogom. Izvan razvoja
        # aplikacija zato ne kreće s javnim ni s kratkim ključem: bolje da ne radi
        # nego da radi nezaštićena.
        if self.ENV != "dev" and (
            self.JWT_SECRET in PUBLIC_SECRETS or len(self.JWT_SECRET) < 32
        ):
            raise ValueError(
                "JWT_SECRET mora biti tajan i imati barem 32 znaka; "
                "stvoriti ga naredbom openssl rand -hex 32"
            )
        return self

    @property
    def is_dev(self) -> bool:
        return self.ENV == "dev"


settings = Settings()
