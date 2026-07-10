from pydantic import BaseModel, Field
from datetime import datetime


class ProcessContractCreate(BaseModel):
    site_name: str = Field(..., description="사업장명")
    process: str = Field(..., description="공정명")
    line: str | None = Field(None, description="라인")
    contract_hours: float | None = Field(None, description="계약 작업시간(시간 단위)")
    is_approximate: bool = Field(False, description="근사값 여부 (약 X시간)")


class ProcessContractResponse(BaseModel):
    id: int
    site_name: str
    process: str
    line: str | None
    contract_hours: float | None
    is_approximate: bool
    created_at: datetime

    model_config = {"from_attributes": True}
