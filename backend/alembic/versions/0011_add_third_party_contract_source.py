"""Add third_party_contract to contract_source enum."""

from alembic import op

revision = "0011_add_third_party_contract_source"
down_revision = "0010_migrate_to_postgres"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE contract_source ADD VALUE IF NOT EXISTS 'third_party_contract'"
        )


def downgrade() -> None:
    pass
