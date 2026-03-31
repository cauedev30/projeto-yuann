from __future__ import annotations

from pathlib import Path


def test_alembic_history_tracks_contract_analysis_correction_columns() -> None:
    versions_dir = Path(__file__).resolve().parents[2] / "alembic" / "versions"
    migration_sources = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(versions_dir.glob("*.py"))
    )

    assert "corrected_text" in migration_sources
    assert "corrections_summary" in migration_sources
