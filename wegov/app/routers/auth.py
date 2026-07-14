from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.deps import get_current_worker, require_admin
from jose import JWTError
from app.models.worker import Worker
from app.schemas.auth import LoginRequest, ActivateRequest, TokenResponse, RefreshRequest, ChangePasswordRequest, DefaultPasswordSetRequest

router = APIRouter(prefix="/auth", tags=["인증"])


def _get_default_password(role: str) -> str:
    if role == "admin":
        return settings.default_password_admin
    return settings.default_password_worker


def _verify_login_password(input_password: str, worker: Worker) -> bool:
    if worker.password_hash:
        return verify_password(input_password, worker.password_hash)
    # 개인 비밀번호 미설정 시 역할별 초기값으로 검증
    return input_password == _get_default_password(worker.role)


@router.post("/login", response_model=TokenResponse, summary="로그인")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    # birth_date 6자리 입력 시 앞에 '19' 또는 '20' 붙여 8자리로 정규화
    birth_date = body.birth_date
    if len(birth_date) == 6:
        prefix = "20" if int(birth_date[:2]) <= 25 else "19"
        birth_date = prefix + birth_date

    result = await db.execute(
        select(Worker).where(
            Worker.name == body.name,
            Worker.birth_date == birth_date,
            Worker.active_filter(),
        )
    )
    worker = result.scalars().first()

    # 비밀번호 생략 시 birth_date(정규화 전 원본)를 비밀번호로 사용
    password = body.password if body.password is not None else body.birth_date

    if worker is None or not _verify_login_password(password, worker):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이름, 생년월일 또는 비밀번호가 올바르지 않습니다.",
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
    result = await db.execute(
        select(Worker).where(Worker.name == body.name)
    )
    worker = result.scalars().first()

    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="등록되지 않은 직원입니다.")

    if worker.resident_number_hash is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="계정 활성화 정보가 없습니다. 관리자에게 문의하세요.")

    if not verify_password(body.resident_number, worker.resident_number_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="주민번호가 올바르지 않습니다.")

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


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT, summary="개인 비밀번호 변경")
async def change_password(
    body: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_worker: Worker = Depends(get_current_worker),
):
    if not _verify_login_password(body.current_password, current_worker):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="현재 비밀번호가 올바르지 않습니다.")

    current_worker.password_hash = hash_password(body.new_password)
    await db.commit()


@router.patch("/default-password", status_code=status.HTTP_204_NO_CONTENT, summary="역할별 초기 비밀번호 설정 (관리자)")
async def set_default_password(
    body: DefaultPasswordSetRequest,
    _=Depends(require_admin),
):
    # 초기 비밀번호는 환경변수로 관리 — 런타임 변경은 지원하지 않음
    # 변경하려면 Railway 환경변수(DEFAULT_PASSWORD_WORKER / DEFAULT_PASSWORD_ADMIN)를 직접 수정
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="초기 비밀번호는 Railway 환경변수(DEFAULT_PASSWORD_WORKER / DEFAULT_PASSWORD_ADMIN)에서 변경하세요.",
    )
