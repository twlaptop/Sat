from pydantic import BaseModel, Field
from datetime import datetime


class SiteCreate(BaseModel):
    name: str = Field(..., description="사업장명 (예: 삼성전자 온양사업장)")
    company: str | None = Field(None, description="고객사명 (예: 삼성전자, SK하이닉스)")


class SiteUpdate(BaseModel):
    name: str | None = None
    company: str | None = None


class SiteResponse(BaseModel):
    id: int
    name: str
    company: str | None
    created_at: datetime

    class Config:
        from_attributes = True
