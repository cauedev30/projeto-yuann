from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_contract_lifecycle_fields"
down_revision = "0006_add_user_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "contracts",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "contracts",
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "contracts",
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "contracts",
        sa.Column("last_analyzed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("contracts", "last_analyzed_at")
    op.drop_column("contracts", "last_accessed_at")
    op.drop_column("contracts", "activated_at")
    op.drop_column("contracts", "is_active")
