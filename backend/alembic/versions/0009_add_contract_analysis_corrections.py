from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0009_contract_analysis_corrections"
down_revision = "0008_contract_version_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    existing_columns = {column["name"] for column in inspect(bind).get_columns("contract_analyses")}

    if "corrected_text" not in existing_columns:
        op.add_column("contract_analyses", sa.Column("corrected_text", sa.Text(), nullable=True))
    if "corrections_summary" not in existing_columns:
        op.add_column("contract_analyses", sa.Column("corrections_summary", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("contract_analyses", "corrections_summary")
    op.drop_column("contract_analyses", "corrected_text")
