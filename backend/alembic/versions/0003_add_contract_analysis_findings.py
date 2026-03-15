from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_contract_analysis_findings"
down_revision = "0002_contract_version_extraction_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contract_analysis_findings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("clause_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("current_summary", sa.Text(), nullable=False),
        sa.Column("policy_rule", sa.Text(), nullable=False),
        sa.Column("risk_explanation", sa.Text(), nullable=False),
        sa.Column("suggested_adjustment_direction", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["contract_analyses.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("contract_analysis_findings")
