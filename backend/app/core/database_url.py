from __future__ import annotations


def resolve_database_url(
    database_url: str | None = None,
    *,
    env_database_url: str | None = None,
    local_default: str = "sqlite:///./legaltech.db",
) -> str:
    resolved_database_url = database_url or env_database_url or local_default

    if resolved_database_url.startswith("postgresql://"):
        return resolved_database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    if resolved_database_url.startswith("postgres://"):
        return resolved_database_url.replace("postgres://", "postgresql+psycopg://", 1)

    return resolved_database_url
