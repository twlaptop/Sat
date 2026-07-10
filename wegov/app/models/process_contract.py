from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Float, DateTime, Boolean, text
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class ProcessContract(Base):
    __tablename__ = "process_contracts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    site_name: Mapped[str] = mapped_column(String(100), nullable=False)       # 사업장명 (예: 삼성전자 온양사업장)
    process: Mapped[str] = mapped_column(String(100), nullable=False)         # 공정명 (예: COW, AVI, Mold)
    line: Mapped[str | None] = mapped_column(String(50), nullable=True)       # 라인 (예: 1L, C1, C동)
    contract_hours: Mapped[float | None] = mapped_column(Float, nullable=True) # 계약 작업시간(시간 단위) — None이면 미정
    is_approximate: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )  # True면 "약 X시간" 형태의 근사값
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
