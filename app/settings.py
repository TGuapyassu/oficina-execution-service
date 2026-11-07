from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    database_url: str = Field(
        default="sqlite:///:memory:",
        validation_alias="DATABASE_URL",
    )
    rabbitmq_url: str = Field(default="", validation_alias="RABBITMQ_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    os_service_url: str = Field(default="http://localhost:8001", validation_alias="OS_SERVICE_URL")
    internal_service_key: str = Field(default="dev-internal-key", validation_alias="INTERNAL_SERVICE_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
