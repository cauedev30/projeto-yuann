from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_contract_version_extraction_metadata"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("contract_versions", sa.Column("extraction_metadata", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("contract_versions", "extraction_metadata")
