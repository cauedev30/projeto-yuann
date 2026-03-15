from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_contract_archive_fields"
down_revision = "0003_contract_analysis_findings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("contracts", sa.Column("signature_date", sa.Date(), nullable=True))
    op.add_column("contracts", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("contracts", sa.Column("end_date", sa.Date(), nullable=True))
    op.add_column("contracts", sa.Column("term_months", sa.Integer(), nullable=True))
    op.add_column("contracts", sa.Column("financial_terms", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("contracts", "financial_terms")
    op.drop_column("contracts", "term_months")
    op.drop_column("contracts", "end_date")
    op.drop_column("contracts", "start_date")
    op.drop_column("contracts", "signature_date")
