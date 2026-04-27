"""Add RBAC role, contract ownership, and drop analysis tables.

Revision ID: 0014
Revises: 0013
Create Date: 2026-04-27

"""

from alembic import op
import sqlalchemy as sa

revision = "0014_consultative_rbac"
down_revision = "0013_add_performance_indexes"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        with op.batch_alter_table("users") as batch_op:
            batch_op.add_column(
                sa.Column("role", sa.String(20), nullable=False, server_default="user")
            )
        with op.batch_alter_table("contracts") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "owner_id",
                    sa.String(36),
                    sa.ForeignKey("users.id", ondelete="SET NULL"),
                    nullable=True,
                )
            )
    else:
        op.add_column(
            "users",
            sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        )
        op.add_column(
            "contracts",
            sa.Column(
                "owner_id",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )

    op.create_index("idx_contracts_owner_id", "contracts", ["owner_id"])
    op.drop_table("contract_analysis_findings")
    op.drop_table("contract_analyses")


def downgrade():
    op.drop_index("idx_contracts_owner_id", table_name="contracts")

    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        with op.batch_alter_table("contracts") as batch_op:
            batch_op.drop_column("owner_id")
        with op.batch_alter_table("users") as batch_op:
            batch_op.drop_column("role")
    else:
        op.drop_column("contracts", "owner_id")
        op.drop_column("users", "role")

    # Re-create analysis tables (minimal, acceptable to omit full reconstruction)
    op.create_table(
        "contract_analyses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("contract_id", sa.String(36), sa.ForeignKey("contracts.id", ondelete="CASCADE")),
        sa.Column("contract_version_id", sa.String(36), sa.ForeignKey("contract_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_version", sa.String(50), nullable=False),
        sa.Column("status", sa.Enum("pending", "completed", "failed", name="analysis_status"), nullable=False),
        sa.Column("contract_risk_score", sa.Numeric(5, 2)),
        sa.Column("raw_payload", sa.JSON()),
        sa.Column("corrected_text", sa.Text()),
        sa.Column("corrections_summary", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_table(
        "contract_analysis_findings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("analysis_id", sa.String(36), sa.ForeignKey("contract_analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clause_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("current_summary", sa.Text(), nullable=False),
        sa.Column("policy_rule", sa.Text(), nullable=False),
        sa.Column("risk_explanation", sa.Text(), nullable=False),
        sa.Column("suggested_adjustment_direction", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
