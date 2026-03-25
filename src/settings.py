# Environment-variable-based settings.
# Values that change between deployments and must come from
# ENV variables or a .env file belong here.
# Per-environment static configuration lives in config.py instead.

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
