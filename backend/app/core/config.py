from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(alias="APP_ENV")
    app_name: str = Field(alias="APP_NAME")
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    s3_endpoint: str = Field(alias="S3_ENDPOINT")
    s3_access_key: str = Field(alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(alias="S3_SECRET_KEY")
    s3_bucket: str = Field(alias="S3_BUCKET")
    s3_region: str = Field(alias="S3_REGION")
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    ocr_language: str = Field(alias="OCR_LANGUAGE")
    alerts_from_email: str = Field(alias="ALERTS_FROM_EMAIL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )


def get_settings(**overrides: str) -> Settings:
    return Settings(**overrides)
