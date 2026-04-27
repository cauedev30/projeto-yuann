"""Add contract_embeddings table with pgvector."""

from alembic import op
import sqlalchemy as sa

revision = "0012_add_contract_embeddings_table"
down_revision = "0011_add_third_party_contract_source"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "contract_embeddings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "contract_id",
            sa.String(36),
            sa.ForeignKey("contracts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_type", sa.String(50), nullable=False),
        sa.Column("chunk_text", sa.Text, nullable=False),
        sa.Column("embedding", sa.Text, nullable=False),
        sa.Column("metadata_json", sa.JSON),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("contract_embeddings")
