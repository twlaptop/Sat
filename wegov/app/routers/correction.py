from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.correction import Correction
from app.models.work_record import WorkRecord
from app.schemas.correction import CorrectionRequest, CorrectionResolveRequest, CorrectionResponse

router = APIRouter(prefix="/corrections", tags=["수정 요청"])

VALID_TYPES = {"CHECKIN_MISS", "CHECKOUT_MISS", "WRONG_PRESS", "LONG_STAY"}


@router.post("", response_model=CorrectionResponse, status_code=status.HTTP_201_CREATED, summary="수정 요청 등록")
async def create_correction(
    body: CorrectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    if body.correction_type not in VALID_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 수정 유형입니다. 허용값: {', '.join(VALID_TYPES)}",
        )
    correction = Correction(worker_id=int(current_user), **body.model_dump())
    db.add(correction)
    await db.commit()
    await db.refresh(correction)
    return correction


@router.get("/me", response_model=list[CorrectionResponse], summary="내 수정 요청 목록")
async def get_my_corrections(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(
        select(Correction)
        .where(Correction.worker_id == int(current_user))
        .order_by(Correction.created_at.desc())
    )
    return result.scalars().all()


@router.get("/pending", response_model=list[CorrectionResponse], summary="승인 대기 목록 (관리자/리더)")
async def get_pending_corrections(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(
        select(Correction)
        .where(Correction.status == "pending")
        .order_by(Correction.created_at)
    )
    return result.scalars().all()


@router.post("/{correction_id}/resolve", response_model=CorrectionResponse, summary="수정 요청 승인/반려 (관리자)")
async def resolve_correction(
    correction_id: int,
    body: CorrectionResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    if body.action not in {"approve", "reject"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="action은 approve 또는 reject 이어야 합니다.")

    result = await db.execute(select(Correction).where(Correction.id == correction_id))
    correction = result.scalar_one_or_none()
    if correction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="수정 요청을 찾을 수 없습니다.")
    if correction.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 처리된 요청입니다.")

    correction.status = "approved" if body.action == "approve" else "rejected"
    correction.resolved_by = current_user
    correction.resolved_at = datetime.now(timezone.utc)

    if body.action == "approve":
        await _apply_correction(correction, db)

    await db.commit()
    await db.refresh(correction)
    return correction


async def _apply_correction(correction: Correction, db: AsyncSession) -> None:
    """승인 시 실제 기록에 반영 — Silent Failure 없이 명시적 예외 발생"""

    if correction.correction_type == "CHECKIN_MISS":
        if not correction.requested_checkin_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="입실 누락 수정에는 요청 입실 시각이 필요합니다.")
        result = await db.execute(
            select(WorkRecord)
            .where(WorkRecord.worker_id == correction.worker_id)
            .order_by(WorkRecord.round.desc()).limit(1)
        )
        last = result.scalar_one_or_none()
        db.add(WorkRecord(
            worker_id=correction.worker_id,
            round=(last.round + 1) if last else 1,
            site_name=correction.site_name or "",
            process=correction.process or "",
            shift_type=correction.shift_type or "D",
            checkin_at=correction.requested_checkin_at,
            checkout_at=correction.requested_checkout_at,
            note="관리자 승인 — 입실 누락 수정",
        ))

    elif correction.correction_type == "CHECKOUT_MISS":
        if not correction.record_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="퇴실 누락 수정에는 대상 출입기록 ID가 필요합니다.")
        if not correction.requested_checkout_fix:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="퇴실 누락 수정에는 요청 퇴실 시각이 필요합니다.")
        result = await db.execute(select(WorkRecord).where(WorkRecord.id == correction.record_id))
        record = result.scalar_one_or_none()
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="대상 출입기록을 찾을 수 없습니다.")
        record.checkout_at = correction.requested_checkout_fix
        record.note = "관리자 승인 — 퇴실 누락 수정"

    elif correction.correction_type == "WRONG_PRESS":
        if not correction.record_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="잘못 누름 수정에는 대상 출입기록 ID가 필요합니다.")
        result = await db.execute(select(WorkRecord).where(WorkRecord.id == correction.record_id))
        record = result.scalar_one_or_none()
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="대상 출입기록을 찾을 수 없습니다.")
        # 물리 삭제 금지 — is_voided=True로 무효 처리 (원본 기록 보존)
        record.is_voided = True
        record.note = "관리자 승인 — 잘못 누름 무효 처리"
