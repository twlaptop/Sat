import logging
from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import logger

logging.getLogger("passlib").setLevel(logging.ERROR)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def create_refresh_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=30)
    return jwt.encode(
        {"sub": subject, "exp": expire, "iat": now, "type": "refresh"},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expire, "iat": now},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except ExpiredSignatureError:
        if settings.env == "development":
            logger.warning("[JWT] 토큰 만료 — 클라이언트 갱신 필요")
        raise
    except JWTError as e:
        if settings.env == "development":
            logger.warning("[JWT] 서명 검증 실패: %s", e)
        raise

    sub: str | None = payload.get("sub")
    if sub is None:
        if settings.env == "development":
            logger.warning("[JWT] sub 클레임 누락")
        raise JWTError("sub missing")
    iat: int | None = payload.get("iat")
    return sub, iat