from pydantic import BaseModel, Field
from datetime import datetime


class NoticeCreate(BaseModel):
    title: str = Field(..., description="공지 제목")
    content: str | None = Field(None, description="공지 내용")


class NoticeUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str | None
    created_by: str | None
    created_at: datetime

    class Config:
        from_attributes = True
