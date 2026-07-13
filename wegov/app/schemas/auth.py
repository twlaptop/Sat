from pydantic import BaseModel, Field


# 로그인 요청 — 이름 + 생년월일 8자리 + 비밀번호
class LoginRequest(BaseModel):
    name: str = Field(..., description="직원 이름")
    birth_date: str = Field(..., min_length=8, max_length=8, description="생년월일 8자리 (예: 19950110)")
    password: str = Field(..., description="비밀번호 (worker/leader: 숫자 4자리, admin: 8자 이상)")


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


# 개인 비밀번호 변경
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., description="새 비밀번호")


# 역할별 초기 비밀번호 설정 (admin 전용)
class DefaultPasswordSetRequest(BaseModel):
    role: str = Field(..., description="역할 (worker / leader / admin)")
    password: str = Field(..., description="초기 비밀번호")
