from pydantic import BaseModel, model_validator
from datetime import datetime, timezone, timedelta

_KST = timezone(timedelta(hours=9))

# 근무표 유형별 지각 기준시각 (HHMM 정수 기준)
_LATE_THRESHOLD = {
    "D": 600,   # 06:00
    "주": 600,
    "S": 1800,  # 18:00
    "야": 1800,
    "O": 800,   # 08:00
}


class RecordResponse(BaseModel):
    id: int
    worker_id: int
    round: int
    site_name: str
    process: str
    shift_type: str
    checkin_at: datetime
    checkout_at: datetime | None
    duration_minutes: int | None
    is_voided: bool
    note: str | None
    is_late: bool = False

    @model_validator(mode="after")
    def calc_is_late(self):
        threshold = _LATE_THRESHOLD.get(self.shift_type)
        if threshold and self.checkin_at:
            kst = self.checkin_at.astimezone(_KST)
            hhmm = kst.hour * 100 + kst.minute
            self.is_late = hhmm > threshold
        return self

    class Config:
        from_attributes = True
