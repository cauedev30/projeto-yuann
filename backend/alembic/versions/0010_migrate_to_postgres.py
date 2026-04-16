"""Migrate to PostgreSQL — enable pgvector, fix JSON columns."""

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    with op.batch_alter_table("contracts") as batch_op:
        batch_op.alter_column("parties", type_=sa.JSON, existing_type=sa.Text)
        batch_op.alter_column("financial_terms", type_=sa.JSON, existing_type=sa.Text)

    with op.batch_alter_table("contract_versions") as batch_op:
        batch_op.alter_column(
            "extraction_metadata", type_=sa.JSON, existing_type=sa.Text
        )

    with op.batch_alter_table("contract_analyses") as batch_op:
        batch_op.alter_column("raw_payload", type_=sa.JSON, existing_type=sa.Text)
        batch_op.alter_column(
            "corrections_summary", type_=sa.JSON, existing_type=sa.Text
        )

    with op.batch_alter_table("contract_analysis_findings") as batch_op:
        batch_op.alter_column("metadata_json", type_=sa.JSON, existing_type=sa.Text)


def downgrade() -> None:
    pass
