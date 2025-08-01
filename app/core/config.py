from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = Field("sqlite:///./data/homebudget.db")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
