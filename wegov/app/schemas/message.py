from datetime import datetime
from pydantic import BaseModel, Field


class MessageSend(BaseModel):
    receiver_id: int | None = Field(None, description="수신자 직원 ID — 생략 시 최종관리자에게 자동 전송")
    content: str = Field(..., min_length=1, max_length=2000, description="메시지 내용")


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
