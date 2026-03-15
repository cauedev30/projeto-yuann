from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


contract_source = sa.Enum("third_party_draft", "signed_contract", name="contract_source")
analysis_status = sa.Enum("pending", "completed", "failed", name="analysis_status")
event_type = sa.Enum("renewal", "expiration", "readjustment", "grace_period_end", name="event_type")
notification_channel = sa.Enum("email", "in_app", name="notification_channel")


def upgrade() -> None:
    op.create_table(
        "policies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "contracts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("external_reference", sa.String(length=100), nullable=False, unique=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("parties", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "policy_rules",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("policy_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "contract_versions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_id", sa.String(length=36), nullable=False),
        sa.Column("source", contract_source, nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("text_content", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "contract_analyses",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_id", sa.String(length=36), nullable=True),
        sa.Column("policy_version", sa.String(length=50), nullable=False),
        sa.Column("status", analysis_status, nullable=False),
        sa.Column("contract_risk_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "contract_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", event_type, nullable=False),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.Column("lead_time_days", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_event_id", sa.String(length=36), nullable=False),
        sa.Column("channel", notification_channel, nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False, unique=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["contract_event_id"], ["contract_events.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("contract_events")
    op.drop_table("contract_analyses")
    op.drop_table("contract_versions")
    op.drop_table("policy_rules")
    op.drop_table("contracts")
    op.drop_table("policies")

    notification_channel.drop(op.get_bind(), checkfirst=False)
    event_type.drop(op.get_bind(), checkfirst=False)
    analysis_status.drop(op.get_bind(), checkfirst=False)
    contract_source.drop(op.get_bind(), checkfirst=False)
