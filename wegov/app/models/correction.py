from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class Correction(Base):
    __tablename__ = "corrections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False
    )  # 요청한 직원
    record_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("work_records.id", ondelete="SET NULL"), nullable=True
    )  # 대상 출입기록 (CHECKIN_MISS는 기록 자체가 없어서 nullable)
    correction_type: Mapped[str] = mapped_column(String(20), nullable=False)           # CHECKIN_MISS / CHECKOUT_MISS / WRONG_PRESS / LONG_STAY
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")  # pending / approved / rejected
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)                    # 수정 요청 사유

    # CHECKIN_MISS 전용 — 누락된 입실 정보 직접 입력
    site_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    process: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shift_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    requested_checkin_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requested_checkout_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # CHECKOUT_MISS 전용 — 퇴실 시각 수정 요청
    requested_checkout_fix: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    resolved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)        # 처리한 관리자 JWT sub
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
