from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin, require_leader_or_above
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleResponse

router = APIRouter(prefix="/schedules", tags=["스케줄"])


@router.get("/me", response_model=list[ScheduleResponse], summary="내 스케줄 조회")
async def get_my_schedules(
    target_date: date = Query(default=None, description="조회 날짜 (미입력 시 오늘)"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    worker_id = int(current_user)
    query_date = target_date or date.today()

    result = await db.execute(
        select(Schedule).where(
            Schedule.worker_id == worker_id,
            Schedule.date == query_date,
        )
    )
    return result.scalars().all()


@router.get("/worker/{worker_id}", response_model=list[ScheduleResponse], summary="특정 직원 스케줄 조회 (리더+)")
async def get_worker_schedules(
    worker_id: int,
    target_date: date = Query(default=None, description="조회 날짜 (미입력 시 오늘)"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_leader_or_above),
):
    query_date = target_date or date.today()

    result = await db.execute(
        select(Schedule).where(
            Schedule.worker_id == worker_id,
            Schedule.date == query_date,
        )
    )
    return result.scalars().all()


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED, summary="스케줄 등록 (관리자)")
async def create_schedule(
    body: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    schedule = Schedule(**body.model_dump())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="스케줄 삭제 (관리자)")
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="스케줄을 찾을 수 없습니다.")

    await db.delete(schedule)
    await db.commit()
