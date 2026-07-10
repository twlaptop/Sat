from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.message import Message
from app.models.worker import Worker
from app.schemas.message import MessageSend, MessageResponse

router = APIRouter(prefix="/messages", tags=["엑스티톡"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="메시지 전송")
async def send_message(
    body: MessageSend,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    sender_id = int(current_user)

    result = await db.execute(
        select(Worker).where(Worker.id == body.receiver_id, Worker.active_filter())
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="수신자를 찾을 수 없습니다.")

    msg = Message(sender_id=sender_id, receiver_id=body.receiver_id, content=body.content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.get("/me", response_model=list[MessageResponse], summary="내 메시지 목록 (받은 메시지)")
async def get_my_messages(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    worker_id = int(current_user)
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
    current_user: str = Depends(get_current_user),
):
    me = int(current_user)
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
    current_user: str = Depends(get_current_user),
):
    worker_id = int(current_user)
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
