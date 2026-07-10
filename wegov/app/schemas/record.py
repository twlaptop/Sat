from pydantic import BaseModel
from datetime import datetime


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
    note: str | None

    class Config:
        from_attributes = True
