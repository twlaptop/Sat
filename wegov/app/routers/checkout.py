from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.work_record import WorkRecord
from app.schemas.checkout import CheckoutRequest, CheckoutResponse

router = APIRouter(prefix="/checkout", tags=["퇴실"])


@router.post("", response_model=CheckoutResponse, summary="퇴실")
async def checkout(
    body: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    worker_id = int(current_user)

    # 현재 입실 중인 기록 조회
    result = await db.execute(
        select(WorkRecord).where(
            WorkRecord.worker_id == worker_id,
            WorkRecord.checkout_at.is_(None),
            WorkRecord.is_voided.is_(False),
        )
    )
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="입실 기록이 없습니다. 먼저 입실해주세요.",
        )

    # 퇴실 시각 저장
    record.checkout_at = datetime.now(timezone.utc)
    if body.note:
        record.note = body.note

    await db.commit()
    # duration_minutes는 DB STORED Computed → refresh 후 반영
    await db.refresh(record)
    return record
