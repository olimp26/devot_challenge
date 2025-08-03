from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    reload: bool = Field(True)
    log_level: str = Field("INFO")

    database_url: str = Field("sqlite:///./data/homebudget.db")

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
