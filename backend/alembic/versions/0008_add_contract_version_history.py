from __future__ import annotations

from collections import defaultdict

from alembic import op
import sqlalchemy as sa


revision = "0008_contract_version_history"
down_revision = "0007_contract_lifecycle_fields"
branch_labels = None
depends_on = None


contract_versions = sa.table(
    "contract_versions",
    sa.column("id", sa.String(length=36)),
    sa.column("contract_id", sa.String(length=36)),
    sa.column("version_number", sa.Integer()),
    sa.column("created_at", sa.DateTime(timezone=True)),
)

contract_analyses = sa.table(
    "contract_analyses",
    sa.column("id", sa.String(length=36)),
    sa.column("contract_id", sa.String(length=36)),
    sa.column("contract_version_id", sa.String(length=36)),
    sa.column("created_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    with op.batch_alter_table("contract_versions") as batch_op:
        batch_op.add_column(sa.Column("version_number", sa.Integer(), nullable=True))

    with op.batch_alter_table("contract_analyses") as batch_op:
        batch_op.add_column(sa.Column("contract_version_id", sa.String(length=36), nullable=True))

    bind = op.get_bind()

    version_rows = bind.execute(
        sa.select(
            contract_versions.c.id,
            contract_versions.c.contract_id,
            contract_versions.c.created_at,
        ).order_by(
            contract_versions.c.contract_id,
            contract_versions.c.created_at,
            contract_versions.c.id,
        )
    ).mappings().all()

    versions_by_contract: dict[str, list[dict[str, object]]] = defaultdict(list)
    current_numbers: dict[str, int] = defaultdict(int)

    for row in version_rows:
        contract_id = str(row["contract_id"])
        current_numbers[contract_id] += 1
        version_number = current_numbers[contract_id]
        bind.execute(
            sa.update(contract_versions)
            .where(contract_versions.c.id == row["id"])
            .values(version_number=version_number)
        )
        versions_by_contract[contract_id].append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "version_number": version_number,
            }
        )

    analysis_rows = bind.execute(
        sa.select(
            contract_analyses.c.id,
            contract_analyses.c.contract_id,
            contract_analyses.c.created_at,
        )
        .where(contract_analyses.c.contract_id.is_not(None))
        .order_by(
            contract_analyses.c.contract_id,
            contract_analyses.c.created_at,
            contract_analyses.c.id,
        )
    ).mappings().all()

    for row in analysis_rows:
        contract_id = str(row["contract_id"])
        versions = versions_by_contract.get(contract_id)
        if not versions:
            continue

        matching_versions = [
            version
            for version in versions
            if row["created_at"] is None
            or version["created_at"] is None
            or version["created_at"] <= row["created_at"]
        ]
        chosen_version = matching_versions[-1] if matching_versions else versions[-1]
        bind.execute(
            sa.update(contract_analyses)
            .where(contract_analyses.c.id == row["id"])
            .values(contract_version_id=chosen_version["id"])
        )

    with op.batch_alter_table("contract_versions") as batch_op:
        batch_op.alter_column("version_number", nullable=False)
        batch_op.create_unique_constraint(
            "uq_contract_versions_contract_id_version_number",
            ["contract_id", "version_number"],
        )

    with op.batch_alter_table("contract_analyses") as batch_op:
        batch_op.alter_column("contract_version_id", nullable=False)
        batch_op.create_foreign_key(
            "fk_contract_analyses_contract_version_id_contract_versions",
            "contract_versions",
            ["contract_version_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("contract_analyses") as batch_op:
        batch_op.drop_constraint(
            "fk_contract_analyses_contract_version_id_contract_versions",
            type_="foreignkey",
        )
        batch_op.drop_column("contract_version_id")

    with op.batch_alter_table("contract_versions") as batch_op:
        batch_op.drop_constraint(
            "uq_contract_versions_contract_id_version_number",
            type_="unique",
        )
        batch_op.drop_column("version_number")
