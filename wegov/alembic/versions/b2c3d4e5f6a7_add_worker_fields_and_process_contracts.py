"""add_worker_fields_and_process_contracts

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-10 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # workers 테이블 — 누락 컬럼 추가
    op.add_column("workers", sa.Column("email", sa.String(200), nullable=True))
    op.add_column("workers", sa.Column("english_name", sa.String(100), nullable=True))
    op.add_column("workers", sa.Column("outsourcing_company", sa.String(100), nullable=True))
    op.add_column("workers", sa.Column("probation_end_date", sa.Date(), nullable=True))
    op.add_column("workers", sa.Column("contract_end_date", sa.Date(), nullable=True))
    op.add_column("workers", sa.Column("contract_renewal_date", sa.Date(), nullable=True))
    op.add_column("workers", sa.Column("is_final_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    # process_contracts 테이블 신규 생성
    op.create_table(
        "process_contracts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("site_name", sa.String(100), nullable=False),
        sa.Column("process", sa.String(100), nullable=False),
        sa.Column("line", sa.String(50), nullable=True),
        sa.Column("contract_hours", sa.Float(), nullable=True),
        sa.Column("is_approximate", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_process_contracts_site_process", "process_contracts", ["site_name", "process"])


def downgrade() -> None:
    op.drop_index("ix_process_contracts_site_process", table_name="process_contracts")
    op.drop_table("process_contracts")

    op.drop_column("workers", "is_final_admin")
    op.drop_column("workers", "contract_renewal_date")
    op.drop_column("workers", "contract_end_date")
    op.drop_column("workers", "probation_end_date")
    op.drop_column("workers", "outsourcing_company")
    op.drop_column("workers", "english_name")
    op.drop_column("workers", "email")
