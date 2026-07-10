# ============================================================
# 재료 준비 — 이 파일에서 사용할 도구들을 불러옴
# ============================================================
from __future__ import annotations          # 아직 정의 안 된 클래스도 타입 힌트에 쓸 수 있게 함
from typing import TYPE_CHECKING            # 아래 if TYPE_CHECKING 블록을 쓰기 위한 플래그
from sqlalchemy.orm import Mapped, mapped_column, relationship
#   Mapped        → 컬럼 타입 선언용
#   mapped_column → 실제 컬럼 정의
#   relationship  → 다른 테이블(명부)과 연결
from sqlalchemy import BigInteger, Integer, String, Boolean, ForeignKey, Index, Computed, DateTime, text
#   ForeignKey → 다른 테이블의 id를 참조 (직원 명부의 id를 가리킴)
#   Computed   → DB가 자동으로 계산해서 채워주는 칸 (체류시간 등)
#   Index      → DB 색인(빠른 조회용 탭)
from sqlalchemy.sql import func             # func.now() → DB 서버 현재 시각 사용
from datetime import datetime               # 날짜+시각
from app.core.database import Base          # 모든 모델이 상속받는 기본 양식 (이걸 상속해야 DB 테이블로 인식)

# ============================================================
# 목차 색인 — 실행 시엔 import 안 함, IDE 분석용으로만 사용
# WorkRecord → Worker 단방향 참조 (출입기록이 직원을 가리킴)
# ============================================================
if TYPE_CHECKING:
    from app.models.worker import Worker    # WorkRecord → Worker 참조


class WorkRecord(Base):
    __tablename__ = "work_records"  # DB 안에서 이 테이블을 부르는 이름

    # --------------------------------------------------------
    # 명부 작성 규칙
    # --------------------------------------------------------
    __table_args__ = (
        # 규칙 1: 퇴실(checkout_at)이 없는 기록은 한 직원당 1개만 허용
        #         → 동시에 두 곳에 입실하는 상황 방지
        Index("uq_active_checkin", "worker_id", unique=True,
              postgresql_where=text("checkout_at IS NULL")),
        # 규칙 2: 직원별 입실시각 기준으로 빠르게 조회할 수 있도록 색인 생성
        Index("ix_work_records_worker_checkin", "worker_id", "checkin_at"),
    )

    # --------------------------------------------------------
    # 명부 칸(컬럼) 설계
    # nullable=False → 반드시 채워야 하는 칸
    # nullable=True  → 비워도 되는 칸
    # --------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # 자동증가 고유번호 (중복 불가)
    worker_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False
    )  # 어느 직원의 기록인지 — workers 테이블의 id를 가리킴, 직원 삭제 시 이 기록도 함께 삭제
    round: Mapped[int] = mapped_column(Integer, nullable=False)                        # 오늘 몇 번째 입실인지 (1회차, 2회차 ...)
    site_name: Mapped[str] = mapped_column(String(100), nullable=False)                # 입실한 사업장명 — 작업자가 직접 선택 (예: 삼성전자 온양사업장)
    process: Mapped[str] = mapped_column(String(100), nullable=False)                  # 작업한 공정명 — 작업자가 직접 선택 (예: COW, 4라인 몰드 세정)
    shift_type: Mapped[str] = mapped_column(String(10), nullable=False)                # 근무표 유형: D(데이) / S(스윙) / O(오피스) / 주(주간) / 야(야간)
    checkin_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)        # 입실 버튼 누른 시각
    checkout_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True) # 퇴실 버튼 누른 시각 — 아직 퇴실 안 했으면 비어있음

    # DB가 자동으로 계산해서 저장하는 칸 (체류 분 수)
    # 계산식: (퇴실시각 - 입실시각) → 초 단위로 변환 → 분으로 나눔
    # checkout_at 저장 후 파이썬 객체에 반영하려면 await db.refresh(record) 필수
    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        Computed("(EXTRACT(EPOCH FROM (checkout_at - checkin_at))::int / 60)::int", persisted=True),
    )  # 체류시간 (분) — DB가 자동 계산, 직접 입력 불가

    is_voided: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))  # 무효 처리 여부 — WRONG_PRESS 승인 시 True (물리 삭제 금지, 원본 보존)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)               # 이석 사유 — PM외부대기 / 면담 / 지각 / 반차 / 조퇴 / 누락 등
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # 기록 생성 시각 (DB 서버 시각 기준 자동 저장)

    # --------------------------------------------------------
    # 다른 명부와 연결 (교차 참조)
    # --------------------------------------------------------
    # 이 출입기록의 주인인 직원 — Worker.records 를 통해 양방향 접근 가능
    worker: Mapped["Worker"] = relationship(back_populates="records")
