from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


# 수동 입실 요청
class CheckinRequest(BaseModel):
    site_name: str = Field(..., description="사업장명 (예: 삼성전자 온양사업장)")
    process: str = Field(..., description="공정명 (예: COW, 4라인 몰드 세정)")
    shift_type: Literal["D", "S", "O", "주", "야"] = Field(..., description="근무표 유형: D / S / O / 주 / 야")


# 스케줄 기반 자동 입실 요청
class CheckinFromScheduleRequest(BaseModel):
    schedule_id: int = Field(..., description="오늘 스케줄 ID")
    shift_type: Literal["D", "S", "O", "주", "야"] = Field("D", description="근무표 유형 (기본값: D)")


# 입실 응답
class CheckinResponse(BaseModel):
    id: int
    worker_id: int
    round: int
    site_name: str
    process: str
    shift_type: str
    checkin_at: datetime

    class Config:
        from_attributes = True
