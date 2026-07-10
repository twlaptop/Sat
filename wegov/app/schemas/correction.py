from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class CorrectionRequest(BaseModel):
    correction_type: Literal["CHECKIN_MISS", "CHECKOUT_MISS", "WRONG_PRESS", "LONG_STAY"] = Field(..., description="CHECKIN_MISS / CHECKOUT_MISS / WRONG_PRESS / LONG_STAY")
    record_id: int | None = Field(None, description="대상 출입기록 ID (CHECKIN_MISS는 없을 수 있음)")
    reason: str | None = Field(None, description="수정 요청 사유")
    site_name: str | None = Field(None, description="사업장명 (CHECKIN_MISS)")
    process: str | None = Field(None, description="공정명 (CHECKIN_MISS)")
    shift_type: Literal["D", "S", "O", "주", "야"] | None = Field(None, description="근무표 유형 (CHECKIN_MISS)")
    requested_checkin_at: datetime | None = Field(None, description="요청 입실 시각 (CHECKIN_MISS)")
    requested_checkout_at: datetime | None = Field(None, description="요청 퇴실 시각 (CHECKIN_MISS)")
    requested_checkout_fix: datetime | None = Field(None, description="수정 요청 퇴실 시각 (CHECKOUT_MISS)")


class CorrectionResolveRequest(BaseModel):
    action: str = Field(..., description="approve / reject")


class CorrectionResponse(BaseModel):
    id: int
    worker_id: int
    record_id: int | None
    correction_type: str
    status: str
    reason: str | None
    site_name: str | None
    process: str | None
    shift_type: str | None
    requested_checkin_at: datetime | None
    requested_checkout_at: datetime | None
    requested_checkout_fix: datetime | None
    resolved_by: str | None
    resolved_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
