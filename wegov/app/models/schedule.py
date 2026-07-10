# ============================================================
# 재료 준비 — 이 파일에서 사용할 도구들을 불러옴
# ============================================================
from __future__ import annotations          # 아직 정의 안 된 클래스도 타입 힌트에 쓸 수 있게 함
from typing import TYPE_CHECKING            # 아래 if TYPE_CHECKING 블록을 쓰기 위한 플래그
from sqlalchemy.orm import Mapped, mapped_column, relationship
#   Mapped        → 컬럼 타입 선언용
#   mapped_column → 실제 컬럼 정의
#   relationship  → 다른 테이블(명부)과 연결
from sqlalchemy import BigInteger, String, Date, DateTime, ForeignKey
#   Date       → 날짜만 저장 (근무 날짜)
#   ForeignKey → 직원 명부의 id를 참조
from sqlalchemy.sql import func             # func.now() → DB 서버 현재 시각 사용
from datetime import datetime, date         # datetime: 날짜+시각 / date: 날짜만
from app.core.database import Base          # 모든 모델이 상속받는 기본 양식

# ============================================================
# 목차 색인 — 실행 시엔 import 안 함, IDE 분석용으로만 사용
# ============================================================
if TYPE_CHECKING:
    from app.models.worker import Worker    # Schedule → Worker 참조


class Schedule(Base):
    __tablename__ = "schedules"     # DB 안에서 이 테이블을 부르는 이름

    # --------------------------------------------------------
    # 명부 칸(컬럼) 설계
    # nullable=False → 반드시 채워야 하는 칸
    # nullable=True  → 비워도 되는 칸
    # --------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # 자동증가 고유번호 (중복 불가)
    worker_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False
    )  # 어느 직원의 스케줄인지 — workers 테이블의 id를 가리킴, 직원 삭제 시 스케줄도 함께 삭제
    date: Mapped[date] = mapped_column(Date, nullable=False)                           # 근무 날짜
    company: Mapped[str | None] = mapped_column(String(100), nullable=True)            # 업체명 (예: 삼성전자)
    site: Mapped[str | None] = mapped_column(String(100), nullable=True)               # 근무 위치 (예: P3 라인 A동)
    process: Mapped[str | None] = mapped_column(String(100), nullable=True)            # 공정명 (예: COW, 4라인 몰드 세정)
    task: Mapped[str | None] = mapped_column(String(100), nullable=True)               # 하는 일 (예: 설비 점검)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # 등록 시각 (DB 서버 시각 기준 자동 저장)

    # --------------------------------------------------------
    # 다른 명부와 연결 (교차 참조)
    # --------------------------------------------------------
    # 이 스케줄의 주인인 직원
    worker: Mapped["Worker"] = relationship(back_populates="schedules")
