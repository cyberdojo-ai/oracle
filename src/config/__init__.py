from pydantic import (
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import (
    Literal,
    Self,
)
from src.utils import singleton


@singleton
class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix = "oracle_",
    )

    application_name: str = "Oracle"

    pg_user: str = "postgres"
    pg_pass: str = "postgres"
    pg_host: str = "127.0.0.1"
    pg_port: int = 5432
    pg_db: str = "oracle"

    pg_pool_size: int = 20
    pg_max_overflow: int = 40

    environment: Literal["development", "testing", "staging", "production"] = "development"

    enable_database_telemetry: bool = False
    enable_fastapi_telemetry: bool = False
    enable_httpx_telemetry: bool = False

    enable_all_telemetry: bool = False

    tracing_batch_processor: bool = True

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.enable_all_telemetry:
            self.enable_database_telemetry = True
            self.enable_fastapi_telemetry = True
            self.enable_httpx_telemetry = True

        return self


    def _remove_trailing_slash(self, v: str) -> str:
        if v.endswith("/"):
            return v[:-1]
        return v


config = Config()
