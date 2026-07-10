from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="인증 정보가 올바르지 않습니다.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> tuple[str, int | None]:
    try:
        return decode_access_token(token)
    except JWTError as e:
        if settings.env == "development":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"인증 정보가 올바르지 않습니다. ({type(e).__name__}: {e})",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise _CREDENTIALS_EXCEPTION


async def get_current_worker(
    token_data: tuple = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.worker import Worker
    worker_id, iat = token_data
    result = await db.execute(
        select(Worker).where(Worker.id == int(worker_id), Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 정보가 올바르지 않습니다.")

    # 토큰 발급 시각이 무효화 시각보다 이전이면 차단
    if worker.token_invalidated_at and iat:
        issued_at = datetime.fromtimestamp(iat, tz=timezone.utc)
        if issued_at < worker.token_invalidated_at:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 만료됐습니다. 다시 로그인해주세요.")

    return worker


def require_role(*roles: str):
    """허용 역할 목록을 받아 의존성 함수를 반환합니다.
    사용: Depends(require_role("admin")) 또는 Depends(require_role("leader", "admin"))
    """
    async def _check(worker=Depends(get_current_worker)):
        if worker.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 작업을 수행할 권한이 없습니다.",
            )
        return worker
    return _check


require_admin = require_role("admin")
require_leader_or_above = require_role("leader", "admin")