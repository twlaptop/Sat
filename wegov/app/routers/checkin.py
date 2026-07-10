from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timezone, timedelta

from app.core.database import get_db
from app.core.deps import get_current_worker, require_leader_or_above
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
    current_worker=Depends(get_current_worker),
):
    worker_id = current_worker.id
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
    current_worker=Depends(get_current_worker),
):
    worker_id = current_worker.id
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
        shift_type=body.shift_type,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/today-schedule", summary="오늘 스케줄 조회")
async def get_today_schedule(
    db: AsyncSession = Depends(get_db),
    current_worker=Depends(get_current_worker),
):
    worker_id = current_worker.id
    result = await db.execute(
        select(Schedule).where(
            Schedule.worker_id == worker_id,
            Schedule.date == date.today(),
        )
    )
    schedule = result.scalar_one_or_none()
    return schedule


@router.get("/realtime", summary="실시간 입실 현황 (관리자/리더)")
async def realtime_status(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_leader_or_above),
):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        select(WorkRecord, Worker)
        .join(Worker, WorkRecord.worker_id == Worker.id)
        .where(
            and_(
                WorkRecord.checkout_at.is_(None),
                WorkRecord.is_voided.is_(False),
                WorkRecord.checkin_at >= today_start,
            )
        )
        .order_by(WorkRecord.checkin_at.desc())
    )
    rows = result.all()

    daily_result = await db.execute(
        select(func.count(WorkRecord.id), func.sum(WorkRecord.duration_minutes))
        .where(
            and_(
                WorkRecord.checkin_at >= today_start,
                WorkRecord.is_voided.is_(False),
                WorkRecord.checkout_at.isnot(None),
            )
        )
    )
    daily = daily_result.one()

    return {
        "current_checkin_count": len(rows),
        "daily_total_entries": daily[0] or 0,
        "daily_total_minutes": daily[1] or 0,
        "current_workers": [
            {
                "worker_id": record.worker_id,
                "name": worker.name,
                "team": worker.team,
                "site_name": record.site_name,
                "process": record.process,
                "checkin_at": record.checkin_at,
                "round": record.round,
            }
            for record, worker in rows
        ],
    }
