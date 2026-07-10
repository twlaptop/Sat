from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.worker import Worker
from app.models.work_record import WorkRecord
from app.models.schedule import Schedule
from app.schemas.checkin import CheckinRequest, CheckinFromScheduleRequest, CheckinResponse

router = APIRouter(prefix="/checkin", tags=["입실"])


async def _get_worker(worker_id: int, db: AsyncSession) -> Worker:
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id, Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="직원 정보를 찾을 수 없습니다.")
    return worker


async def _check_already_checkedin(worker_id: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(WorkRecord).where(
            WorkRecord.worker_id == worker_id,
            WorkRecord.checkout_at.is_(None),
            WorkRecord.is_voided.is_(False),
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 입실 중입니다. 퇴실 후 다시 입실해주세요.",
        )


async def _next_round(worker_id: int, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count(WorkRecord.id)).where(
            WorkRecord.worker_id == worker_id,
            func.date(WorkRecord.checkin_at) == date.today(),
            WorkRecord.is_voided.is_(False),
        )
    )
    return (result.scalar() or 0) + 1


@router.post("/manual", response_model=CheckinResponse, summary="수동 입실")
async def checkin_manual(
    body: CheckinRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    worker_id = int(current_user)
    await _get_worker(worker_id, db)
    await _check_already_checkedin(worker_id, db)
    round_no = await _next_round(worker_id, db)

    record = WorkRecord(
        worker_id=worker_id,
        round=round_no,
        site_name=body.site_name,
        process=body.process,
        shift_type=body.shift_type,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.post("/from-schedule", response_model=CheckinResponse, summary="스케줄 기반 자동 입실")
async def checkin_from_schedule(
    body: CheckinFromScheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    worker_id = int(current_user)
    await _get_worker(worker_id, db)
    await _check_already_checkedin(worker_id, db)

    # 스케줄 조회
    result = await db.execute(
        select(Schedule).where(
            Schedule.id == body.schedule_id,
            Schedule.worker_id == worker_id,
            Schedule.date == date.today(),
        )
    )
    schedule = result.scalar_one_or_none()
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="오늘 스케줄을 찾을 수 없습니다.")

    round_no = await _next_round(worker_id, db)

    record = WorkRecord(
        worker_id=worker_id,
        round=round_no,
        site_name=schedule.site or "",
        process=schedule.process or "",
        shift_type="D",  # 스케줄에 shift_type 없으면 기본값 D
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/today-schedule", summary="오늘 스케줄 조회")
async def get_today_schedule(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    worker_id = int(current_user)
    result = await db.execute(
        select(Schedule).where(
            Schedule.worker_id == worker_id,
            Schedule.date == date.today(),
        )
    )
    schedule = result.scalar_one_or_none()
    return schedule
