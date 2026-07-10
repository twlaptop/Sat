import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_file() -> str | None:
    env = os.getenv("ENV", "production").lower()
    filename = ".env.dev" if env == "development" else ".env"
    return filename if Path(filename).exists() else None


class Settings(BaseSettings):
    env: str = "production"
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    cors_origins: str = "*"  # 쉼표로 구분된 허용 URL (예: "https://admin.wegov.com,https://app.wegov.com")

    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()