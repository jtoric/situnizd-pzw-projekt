from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env stoji u korijenu repozitorija: api/app/core/config.py -> parents[3]
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "Powerlifting Registrations API"
    ENV: str = "dev"
    DATABASE_URL: str
    JWT_SECRET: str = "change-me"
    JWT_ISSUER: str = "sit-unizd"

    # Varijabla okoline ima prednost pred vrijednošću iz .env datoteke
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()
