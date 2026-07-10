from pydantic import BaseModel, Field


# 로그인 요청 — 이름 + 생년월일 6자리
class LoginRequest(BaseModel):
    name: str = Field(..., description="직원 이름")
    birth_date: str = Field(..., min_length=6, max_length=6, description="생년월일 6자리 (예: 950110)")


# 계정 최초 활성화 요청 — 이름 + 주민번호 평문
class ActivateRequest(BaseModel):
    name: str = Field(..., description="직원 이름")
    resident_number: str = Field(..., description="주민번호 평문 (DB의 해시값과 대조)")


# 토큰 응답
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    worker_id: int
    name: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="로그인 시 받은 refresh_token")
