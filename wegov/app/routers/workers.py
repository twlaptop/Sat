from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import hash_password
from app.models.worker import Worker
from app.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse

router = APIRouter(prefix="/workers", tags=["근로자 관리"])


@router.get("", response_model=list[WorkerResponse], summary="재직자 목록 조회")
async def list_workers(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(
        select(Worker).where(Worker.active_filter()).order_by(Worker.name)
    )
    return result.scalars().all()


@router.get("/{worker_id}", response_model=WorkerResponse, summary="직원 상세 조회")
async def get_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id, Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="직원을 찾을 수 없습니다.")
    return worker


@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED, summary="직원 등록 (관리자)")
async def create_worker(
    body: WorkerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    data = body.model_dump()
    # 주민번호가 평문으로 들어오면 해시 처리
    if data.get("resident_number_hash") and not data["resident_number_hash"].startswith("$2b$"):
        data["resident_number_hash"] = hash_password(data["resident_number_hash"])

    worker = Worker(**data)
    db.add(worker)
    await db.commit()
    await db.refresh(worker)
    return worker


@router.patch("/{worker_id}", response_model=WorkerResponse, summary="직원 정보 수정 (관리자)")
async def update_worker(
    worker_id: int,
    body: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id, Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="직원을 찾을 수 없습니다.")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(worker, field, value)

    await db.commit()
    await db.refresh(worker)
    return worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT, summary="직원 퇴사 처리 (관리자) — soft delete")
async def deactivate_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id, Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="직원을 찾을 수 없습니다.")

    worker.is_active = False
    worker.status = "퇴사"
    await db.commit()
