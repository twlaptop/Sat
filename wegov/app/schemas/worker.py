from pydantic import BaseModel, Field
from datetime import date, datetime


class WorkerCreate(BaseModel):
    name: str = Field(..., description="이름")
    company: str = Field(..., description="소속 협력업체명")
    phone: str | None = Field(None, description="전화번호")
    role: str = Field("worker", description="권한: worker / leader / admin")
    status: str = Field("입사예정", description="재직상태")
    work_status: str | None = Field(None, description="업무진행상태")
    team: str | None = Field(None, description="팀")
    group_name: str | None = Field(None, description="그룹")
    squad: str | None = Field(None, description="조")
    line: str | None = Field(None, description="라인")
    birth_date: str | None = Field(None, min_length=6, max_length=6, description="생년월일 6자리")
    resident_number_hash: str | None = Field(None, description="주민번호 bcrypt 해시")
    expected_hire_date: date | None = Field(None, description="입사예정일")
    blood_type: str | None = Field(None, description="혈액형")
    gender: str | None = Field(None, description="성별")
    job_title: str | None = Field(None, description="직무명")


class WorkerUpdate(BaseModel):
    phone: str | None = None
    role: str | None = None
    status: str | None = None
    work_status: str | None = None
    team: str | None = None
    group_name: str | None = None
    squad: str | None = None
    line: str | None = None
    birth_date: str | None = None
    expected_hire_date: date | None = None
    blood_type: str | None = None
    gender: str | None = None
    job_title: str | None = None


class WorkerResponse(BaseModel):
    id: int
    name: str
    company: str
    phone: str | None
    role: str
    status: str
    work_status: str | None
    team: str | None
    group_name: str | None
    squad: str | None
    line: str | None
    birth_date: str | None
    expected_hire_date: date | None
    blood_type: str | None
    gender: str | None
    job_title: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
