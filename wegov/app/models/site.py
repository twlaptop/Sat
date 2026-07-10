# ============================================================
# 재료 준비 — 이 파일에서 사용할 도구들을 불러옴
# ============================================================
from __future__ import annotations          # 아직 정의 안 된 클래스도 타입 힌트에 쓸 수 있게 함
from sqlalchemy.orm import Mapped, mapped_column
#   Mapped        → 컬럼 타입 선언용
#   mapped_column → 실제 컬럼 정의
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.sql import func             # func.now() → DB 서버 현재 시각 사용
from datetime import datetime               # 날짜+시각
from app.core.database import Base          # 모든 모델이 상속받는 기본 양식


class Site(Base):
    __tablename__ = "sites"     # DB 안에서 이 테이블을 부르는 이름

    # --------------------------------------------------------
    # 명부 칸(컬럼) 설계
    # nullable=False → 반드시 채워야 하는 칸
    # nullable=True  → 비워도 되는 칸
    # --------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # 자동증가 고유번호 (중복 불가)
    name: Mapped[str] = mapped_column(String(100), nullable=False)                     # 사업장명 (예: 삼성전자 온양사업장, SKHynix 청주사업장)
    company: Mapped[str | None] = mapped_column(String(100), nullable=True)            # 고객사명 (예: 삼성전자, SK하이닉스, 하나마이크론)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # 등록 시각 (DB 서버 시각 기준 자동 저장)
