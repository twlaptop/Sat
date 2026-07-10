from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_worker, require_admin
from app.models.notice import Notice
from app.schemas.notice import NoticeCreate, NoticeUpdate, NoticeResponse

router = APIRouter(prefix="/notices", tags=["공지사항"])


@router.get("", response_model=list[NoticeResponse], summary="공지사항 목록 조회")
async def list_notices(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_worker),
):
    offset = (page - 1) * limit
    result = await db.execute(select(Notice).order_by(Notice.created_at.desc()).offset(offset).limit(limit))
    return result.scalars().all()


@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED, summary="공지사항 등록 (관리자)")
async def create_notice(
    body: NoticeCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    notice = Notice(**body.model_dump(), created_by=str(admin.id))
    db.add(notice)
    await db.commit()
    await db.refresh(notice)
    return notice


@router.patch("/{notice_id}", response_model=NoticeResponse, summary="공지사항 수정 (관리자)")
async def update_notice(
    notice_id: int,
    body: NoticeUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Notice).where(Notice.id == notice_id))
    notice = result.scalar_one_or_none()
    if notice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="공지사항을 찾을 수 없습니다.")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(notice, field, value)

    await db.commit()
    await db.refresh(notice)
    return notice


@router.delete("/{notice_id}", status_code=status.HTTP_204_NO_CONTENT, summary="공지사항 삭제 (관리자)")
async def delete_notice(
    notice_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Notice).where(Notice.id == notice_id))
    notice = result.scalar_one_or_none()
    if notice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="공지사항을 찾을 수 없습니다.")

    await db.delete(notice)
    await db.commit()
