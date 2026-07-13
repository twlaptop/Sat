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
    jwt_access_token_expire_minutes: int = 120
    cors_origins: str = "*"  # 쉼표로 구분된 허용 URL (예: "https://admin.wegov.com,https://app.wegov.com")
    default_password_worker: str = "1234"   # worker/leader 역할 초기 비밀번호
    default_password_admin: str = "Admin1234!"  # admin 역할 초기 비밀번호

    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()