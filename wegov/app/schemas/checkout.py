from pydantic import BaseModel, Field
from datetime import datetime


# 퇴실 시 이석 사유 추가 (선택)
class CheckoutRequest(BaseModel):
    note: str | None = Field(None, description="이석 사유 (선택): PM외부대기 / 면담 / 지각 / 반차 / 조퇴 / 누락 등")


# 퇴실 응답
class CheckoutResponse(BaseModel):
    id: int
    worker_id: int
    round: int
    site_name: str
    process: str
    checkin_at: datetime
    checkout_at: datetime
    duration_minutes: int | None
    note: str | None

    class Config:
        from_attributes = True
