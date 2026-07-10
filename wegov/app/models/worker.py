# ============================================================
# 재료 준비 — 이 파일에서 사용할 도구들을 불러옴
# ============================================================
from __future__ import annotations          # 아직 정의 안 된 클래스도 타입 힌트에 쓸 수 있게 함
from typing import TYPE_CHECKING            # 아래 if TYPE_CHECKING 블록을 쓰기 위한 플래그
from sqlalchemy.orm import Mapped, mapped_column, relationship
#   Mapped        → 컬럼 타입 선언용
#   mapped_column → 실제 컬럼 정의
#   relationship  → 다른 테이블(명부)과 연결
from sqlalchemy import BigInteger, Integer, String, Boolean, DateTime, Date, Index, select, text
#   BigInteger → id처럼 매우 큰 정수
#   Date       → 날짜만 저장 (입사예정일 등)
#   Index      → DB 색인(빠른 조회용 탭)
#   select     → 조회 쿼리 작성
#   text       → SQL 조건을 직접 문자열로 작성할 때
from sqlalchemy.sql import func             # func.now() → DB 서버 현재 시각 사용
from datetime import datetime, date         # datetime: 날짜+시각 / date: 날짜만
from app.core.database import Base          # 모든 모델이 상속받는 기본 양식 (이걸 상속해야 DB 테이블로 인식)

# ============================================================
# 목차 색인 — 실행 시엔 import 안 함, IDE 분석용으로만 사용
# Worker ↔ WorkRecord, Worker ↔ Notice 서로 참조할 때
# "너 먼저 읽어 / 아니 너 먼저" 충돌을 막기 위한 장치
# ============================================================
if TYPE_CHECKING:
    from app.models.work_record import WorkRecord      # Worker ↔ WorkRecord 양방향 참조
    from app.models.schedule import Schedule           # Worker ↔ Schedule 양방향 참조
    from app.models.worker_document import WorkerDocument  # Worker ↔ WorkerDocument 양방향 참조


class Worker(Base):
    __tablename__ = "workers"   # DB 안에서 이 테이블을 부르는 이름

    # --------------------------------------------------------
    # 명부 작성 규칙
    # --------------------------------------------------------
    __table_args__ = (
        # 규칙 1: 같은 회사에 같은 전화번호는 2명이 있으면 안 됨
        #         단, 전화번호가 없는 사람은 예외
        Index("uq_worker_company_phone", "company", "phone", unique=True,
              postgresql_where=text("phone IS NOT NULL")),
        # 규칙 2: 재직자만 빠르게 찾을 수 있게 별도 색인 탭 생성
        Index("ix_workers_active", "id", postgresql_where=text("is_active = TRUE")),
    )

    # --------------------------------------------------------
    # 명부 칸(컬럼) 설계
    # nullable=False → 반드시 채워야 하는 칸
    # nullable=True  → 비워도 되는 칸
    # server_default → 아무것도 안 입력하면 자동으로 채워지는 기본값
    # --------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # 자동증가 고유번호 (중복 불가)
    name: Mapped[str] = mapped_column(String(100), nullable=False)                     # 이름
    company: Mapped[str] = mapped_column(String(100), nullable=False)                  # 소속 협력업체명
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)               # 전화번호
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="worker")       # 권한: worker(작업자) / leader(리더) / admin(관리자)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="입사예정")    # 재직상태: 재직/수습/수습해지/퇴사예정/휴직/입사예정/신입/퇴사
    work_status: Mapped[str | None] = mapped_column(String(20), nullable=True)         # 업무진행상태: 정상근무 / 수습진행중
    team: Mapped[str | None] = mapped_column(String(50), nullable=True)                # 팀: 제조1팀 / 제조2팀 / 제조3팀 / 경영지원팀
    group_name: Mapped[str | None] = mapped_column(String(50), nullable=True)          # 그룹: 제조1그룹 / 제조2그룹 / 교대직장 등
    squad: Mapped[str | None] = mapped_column(String(20), nullable=True)               # 조: A조 / B조 / C조 / D조 / Day·Swing·OFFICE
    line: Mapped[str | None] = mapped_column(String(50), nullable=True)                # 라인: COW / BLADE / LAMI / FINISH / 4L Mold 등
    birth_date: Mapped[str | None] = mapped_column(String(6), nullable=True)           # 생년월일 6자리 — 매번 로그인 시 비밀번호로 사용 (예: 950110)
    resident_number_hash: Mapped[str | None] = mapped_column(String, nullable=True)    # 주민번호 bcrypt 해시 — 앱 최초 설치 시 본인 확인용 (1회만 사용)
    expected_hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)       # 입사예정일
    blood_type: Mapped[str | None] = mapped_column(String(5), nullable=True)           # 혈액형
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)              # 성별
    job_title: Mapped[str | None] = mapped_column(String(100), nullable=True)          # 직무명
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)              # 개인 이메일
    english_name: Mapped[str | None] = mapped_column(String(100), nullable=True)      # 영문이름
    outsourcing_company: Mapped[str | None] = mapped_column(String(100), nullable=True) # 아웃소싱업체명
    probation_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)       # 수습종료일
    contract_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)        # 계약만료일
    contract_renewal_date: Mapped[date | None] = mapped_column(Date, nullable=True)    # 계약연장예정일
    is_final_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # 최종관리자 여부 (admin 중 최상위 — 최대 3명)
    token_invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True) # 이 시각 이전에 발급된 토큰은 즉시 차단
    profile_image_url: Mapped[str | None] = mapped_column(String, nullable=True)       # 프로필 사진 저장 경로
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)     # 재직 여부 — False = 퇴사 처리 (물리 삭제 금지, 이 값만 바꿈)
    # INSERT 직후 파이썬 객체에는 None → 라우터에서 await db.refresh(worker) 필수
    version: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)  # 수정 충돌 감지용 버전 번호 (수정할 때마다 1씩 증가)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # 등록 시각 (DB 서버 시각 기준 자동 저장)

    # --------------------------------------------------------
    # 다른 명부와 연결 (교차 참조)
    # --------------------------------------------------------
    # 이 직원의 출입기록 목록 — 직원 삭제 시 출입기록도 함께 삭제
    records: Mapped[list["WorkRecord"]] = relationship(
        back_populates="worker", cascade="all, delete-orphan"
    )
    # 이 직원의 근무 스케줄 목록 — 직원 삭제 시 스케줄도 함께 삭제
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="worker", cascade="all, delete-orphan"
    )
    # 이 직원의 서류 파일 목록 — 직원 삭제 시 서류 기록도 함께 삭제
    documents: Mapped[list["WorkerDocument"]] = relationship(
        back_populates="worker", cascade="all, delete-orphan"
    )

    # --------------------------------------------------------
    # 자주 쓰는 기능 버튼 (필터 단축키)
    # --------------------------------------------------------
    @classmethod
    def active_filter(cls):
        # "재직자만" 필터 조건 반환 — select().where(Worker.active_filter()) 형태로 사용
        # 매번 is_active 조건을 직접 쓰는 대신 이 메서드로 통일
        return cls.is_active.is_(True)

    @classmethod
    def active(cls):
        # 재직자 전체 조회 쿼리 반환 — 결과물이 아닌 "쿼리 설계도"
        # await 하면 오류 → await db.execute(Worker.active()) 형태로 사용
        return select(cls).where(cls.active_filter())
