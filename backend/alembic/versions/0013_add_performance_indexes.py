"""Add performance indexes for common queries."""

from alembic import op


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.create_index("ix_contracts_end_date", "contracts", ["end_date"])
        op.create_index("ix_contracts_is_active", "contracts", ["is_active"])
        op.create_index("ix_contracts_status", "contracts", ["status"])
        op.create_index(
            "ix_contract_events_event_date", "contract_events", ["event_date"]
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.drop_index("ix_contracts_end_date")
        op.drop_index("ix_contracts_is_active")
        op.drop_index("ix_contracts_status")
        op.drop_index("ix_contract_events_event_date")
