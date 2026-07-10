from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from app.core.database import get_db
from app.core.deps import get_current_user, require_leader_or_above
from app.models.work_record import WorkRecord
from app.schemas.record import RecordResponse

router = APIRouter(prefix="/records", tags=["출입기록"])


@router.get("/me", response_model=list[RecordResponse], summary="내 출입기록 조회")
async def get_my_records(
    target_date: date = Query(default=None, description="조회 날짜 (미입력 시 오늘)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    worker_id = int(current_user)
    query_date = target_date or date.today()
    offset = (page - 1) * limit

    result = await db.execute(
        select(WorkRecord)
        .where(
            and_(
                WorkRecord.worker_id == worker_id,
                WorkRecord.checkin_at >= query_date,
                WorkRecord.checkin_at < query_date + timedelta(days=1),
                WorkRecord.is_voided.is_(False),
            )
        )
        .order_by(WorkRecord.round)
        .offset(offset).limit(limit)
    )
    return result.scalars().all()


@router.get("/worker/{worker_id}", response_model=list[RecordResponse], summary="특정 직원 출입기록 조회 (관리자/리더)")
async def get_worker_records(
    worker_id: int,
    target_date: date = Query(default=None, description="조회 날짜 (미입력 시 오늘)"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_leader_or_above),
):
    query_date = target_date or date.today()

    result = await db.execute(
        select(WorkRecord)
        .where(
            and_(
                WorkRecord.worker_id == worker_id,
                WorkRecord.checkin_at >= query_date,
                WorkRecord.checkin_at < query_date + timedelta(days=1),
                WorkRecord.is_voided.is_(False),
            )
        )
        .order_by(WorkRecord.round)
    )
    return result.scalars().all()
