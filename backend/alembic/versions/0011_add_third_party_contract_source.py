"""Add third_party_contract to contract_source enum."""

from alembic import op


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE contract_source ADD VALUE IF NOT EXISTS 'third_party_contract'"
        )


def downgrade() -> None:
    pass
