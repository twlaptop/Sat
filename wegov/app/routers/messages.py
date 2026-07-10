from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_worker
from app.models.message import Message
from app.models.worker import Worker
from app.schemas.message import MessageSend, MessageResponse
from app.models.worker import Worker as WorkerModel

router = APIRouter(prefix="/messages", tags=["엑스티톡"])


async def _resolve_receiver(receiver_id: int | None, db) -> int:
    """receiver_id가 없으면 is_final_admin=True인 관리자 중 첫 번째를 반환"""
    if receiver_id is not None:
        result = await db.execute(
            select(WorkerModel).where(WorkerModel.id == receiver_id, WorkerModel.active_filter())
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="수신자를 찾을 수 없습니다.")
        return receiver_id

    result = await db.execute(
        select(WorkerModel).where(
            WorkerModel.role == "admin",
            WorkerModel.is_final_admin.is_(True),
            WorkerModel.active_filter(),
        ).limit(1)
    )
    admin = result.scalars().first()
    if admin is None:
        result = await db.execute(
            select(WorkerModel).where(WorkerModel.role == "admin", WorkerModel.active_filter()).limit(1)
        )
        admin = result.scalars().first()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="수신 가능한 관리자가 없습니다.")
    return admin.id


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="메시지 전송")
async def send_message(
    body: MessageSend,
    db: AsyncSession = Depends(get_db),
    current_worker=Depends(get_current_worker),
):
    sender_id = current_worker.id
    receiver_id = await _resolve_receiver(body.receiver_id, db)

    msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=body.content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.get("/me", response_model=list[MessageResponse], summary="내 메시지 목록 (받은 메시지)")
async def get_my_messages(
    db: AsyncSession = Depends(get_db),
    current_worker=Depends(get_current_worker),
):
    worker_id = current_worker.id
    result = await db.execute(
        select(Message)
        .where(Message.receiver_id == worker_id)
        .order_by(Message.created_at.desc())
    )
    return result.scalars().all()


@router.get("/thread/{other_id}", response_model=list[MessageResponse], summary="특정 상대와의 대화 내역")
async def get_thread(
    other_id: int,
    db: AsyncSession = Depends(get_db),
    current_worker=Depends(get_current_worker),
):
    me = current_worker.id
    result = await db.execute(
        select(Message)
        .where(
            or_(
                and_(Message.sender_id == me, Message.receiver_id == other_id),
                and_(Message.sender_id == other_id, Message.receiver_id == me),
            )
        )
        .order_by(Message.created_at)
    )
    return result.scalars().all()


@router.patch("/{message_id}/read", response_model=MessageResponse, summary="메시지 읽음 처리")
async def mark_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_worker=Depends(get_current_worker),
):
    worker_id = current_worker.id
    result = await db.execute(
        select(Message).where(Message.id == message_id, Message.receiver_id == worker_id)
    )
    msg = result.scalar_one_or_none()
    if msg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="메시지를 찾을 수 없습니다.")

    msg.is_read = True
    await db.commit()
    await db.refresh(msg)
    return msg
