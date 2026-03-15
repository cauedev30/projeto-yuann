from pydantic import ValidationError
import pytest

from app.core.config import Settings


def test_settings_require_database_url() -> None:
    with pytest.raises(ValidationError):
        Settings(
            APP_ENV="development",
            APP_NAME="legaltech-mvp",
            REDIS_URL="redis://localhost:6379/0",
            S3_ENDPOINT="http://localhost:9000",
            S3_ACCESS_KEY="minio",
            S3_SECRET_KEY="minio123",
            S3_BUCKET="contracts",
            S3_REGION="us-east-1",
            OPENAI_API_KEY="test-key",
            OCR_LANGUAGE="por",
            ALERTS_FROM_EMAIL="alerts@example.com",
        )


def test_settings_accept_complete_payload() -> None:
    settings = Settings(
        APP_ENV="development",
        APP_NAME="legaltech-mvp",
        DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/legaltech",
        REDIS_URL="redis://localhost:6379/0",
        S3_ENDPOINT="http://localhost:9000",
        S3_ACCESS_KEY="minio",
        S3_SECRET_KEY="minio123",
        S3_BUCKET="contracts",
        S3_REGION="us-east-1",
        OPENAI_API_KEY="test-key",
        OCR_LANGUAGE="por",
        ALERTS_FROM_EMAIL="alerts@example.com",
    )

    assert settings.database_url.startswith("postgresql+psycopg")
