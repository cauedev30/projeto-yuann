from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_notification_dismissed_at"
down_revision = "0004_contract_archive_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("notifications", "dismissed_at")
