from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.config import settings
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="인증 정보가 올바르지 않습니다.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> str:
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