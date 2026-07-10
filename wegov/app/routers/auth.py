from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_access_token
from jose import JWTError
from app.models.worker import Worker
from app.schemas.auth import LoginRequest, ActivateRequest, TokenResponse, RefreshRequest

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/login", response_model=TokenResponse, summary="로그인")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 이름으로 재직자 조회
    result = await db.execute(
        select(Worker).where(
            Worker.name == body.name,
            Worker.birth_date == body.birth_date,
            Worker.active_filter(),
        )
    )
    worker = result.scalars().first()

    # 직원 없거나 생년월일 불일치 → 동일한 오류 메시지 (보안상 어느 쪽인지 알려주지 않음)
    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이름 또는 생년월일이 올바르지 않습니다.",
        )

    return TokenResponse(
        access_token=create_access_token(str(worker.id)),
        refresh_token=create_refresh_token(str(worker.id)),
        worker_id=worker.id,
        name=worker.name,
        role=worker.role,
    )


@router.post("/activate", response_model=TokenResponse, summary="계정 최초 활성화")
async def activate(body: ActivateRequest, db: AsyncSession = Depends(get_db)):
    # 이름으로 직원 조회 (is_active 무관 — 아직 활성화 전일 수 있음)
    result = await db.execute(
        select(Worker).where(Worker.name == body.name)
    )
    worker = result.scalars().first()

    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록되지 않은 직원입니다.",
        )

    if worker.resident_number_hash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="계정 활성화 정보가 없습니다. 관리자에게 문의하세요.",
        )

    # 주민번호 해시 대조
    if not verify_password(body.resident_number, worker.resident_number_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="주민번호가 올바르지 않습니다.",
        )

    # 활성화 처리
    worker.is_active = True
    await db.commit()
    await db.refresh(worker)

    return TokenResponse(
        access_token=create_access_token(str(worker.id)),
        refresh_token=create_refresh_token(str(worker.id)),
        worker_id=worker.id,
        name=worker.name,
        role=worker.role,
    )


@router.post("/refresh", response_model=TokenResponse, summary="Access Token 갱신 (자동 로그인)")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    from app.core.config import settings
    from jose import jwt as _jwt
    try:
        payload = _jwt.decode(body.refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token이 아닙니다.")
        worker_id = payload.get("sub")
        if not worker_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 refresh token입니다.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 refresh token입니다.")

    result = await db.execute(
        select(Worker).where(Worker.id == int(worker_id), Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 정보가 올바르지 않습니다.")

    return TokenResponse(
        access_token=create_access_token(str(worker.id)),
        refresh_token=create_refresh_token(str(worker.id)),
        worker_id=worker.id,
        name=worker.name,
        role=worker.role,
    )
