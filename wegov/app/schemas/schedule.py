from pydantic import BaseModel, Field
import datetime


class ScheduleCreate(BaseModel):
    worker_id: int = Field(..., description="직원 ID")
    date: datetime.date = Field(..., description="근무 날짜")
    company: str | None = Field(None, description="업체명")
    site: str | None = Field(None, description="근무 위치")
    process: str | None = Field(None, description="공정명")
    task: str | None = Field(None, description="하는 일")


class ScheduleResponse(BaseModel):
    id: int
    worker_id: int
    date: datetime.date
    company: str | None
    site: str | None
    process: str | None
    task: str | None
    created_at: datetime.datetime

    class Config:
        from_attributes = True
