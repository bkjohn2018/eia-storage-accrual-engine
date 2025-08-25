"""Configuration management for EIA Storage Accrual Engine."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    eia_api_key: str | None = None     # optional
    # optionally: log_level: str | None = "INFO"
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="", extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    # lazy, validated on first use only
    return Settings()

# --- Back-compat shim for old imports ---
def __getattr__(name: str):
    # allows:  from eia_sa.config import settings
    if name == "settings":
        return get_settings()
    raise AttributeError(name)
# ----------------------------------------
