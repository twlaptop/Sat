from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Literal

WorkerStatus = Literal["재직", "수습", "수습해지", "퇴사예정", "휴직", "입사예정", "신입", "퇴사"]
WorkerWorkStatus = Literal["입사교육완료", "수습진행중", "수습완료", "퇴사예정", "정상근무"]


class WorkerCreate(BaseModel):
    name: str = Field(..., description="이름")
    company: str = Field(..., description="소속 협력업체명")
    phone: str | None = Field(None, description="전화번호")
    role: Literal["worker", "leader", "admin"] = Field("worker", description="권한: worker / leader / admin")
    status: WorkerStatus = Field("입사예정", description="재직상태")
    work_status: WorkerWorkStatus | None = Field(None, description="업무진행상태")
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
    email: str | None = Field(None, description="개인 이메일")
    english_name: str | None = Field(None, description="영문이름")
    outsourcing_company: str | None = Field(None, description="아웃소싱업체명")
    probation_end_date: date | None = Field(None, description="수습종료일")
    contract_end_date: date | None = Field(None, description="계약만료일")
    contract_renewal_date: date | None = Field(None, description="계약연장예정일")
    is_final_admin: bool = Field(False, description="최종관리자 여부 (admin 중 최상위)")


class WorkerUpdate(BaseModel):
    phone: str | None = None
    role: Literal["worker", "leader", "admin"] | None = None
    status: WorkerStatus | None = None
    work_status: WorkerWorkStatus | None = None
    team: str | None = None
    group_name: str | None = None
    squad: str | None = None
    line: str | None = None
    birth_date: str | None = None
    expected_hire_date: date | None = None
    blood_type: str | None = None
    gender: str | None = None
    job_title: str | None = None
    email: str | None = None
    english_name: str | None = None
    outsourcing_company: str | None = None
    probation_end_date: date | None = None
    contract_end_date: date | None = None
    contract_renewal_date: date | None = None
    is_final_admin: bool | None = None


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
    expected_hire_date: date | None
    blood_type: str | None
    gender: str | None
    job_title: str | None
    email: str | None
    english_name: str | None
    outsourcing_company: str | None
    probation_end_date: date | None
    contract_end_date: date | None
    contract_renewal_date: date | None
    is_final_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
