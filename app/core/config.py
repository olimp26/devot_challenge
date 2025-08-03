from functools import lru_cache
from decimal import Decimal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    reload: bool = Field(True)
    log_level: str = Field("INFO")

    database_url: str = Field("sqlite:///./data/homebudget.db")

    secret_key: str = Field(
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    jwt_algorithm: str = Field("HS256")
    access_token_expire_minutes: int = Field(30)

    initial_transaction_amount: Decimal = Field(
        Decimal("1000.00"),
        description="Predefined amount of money on user account "
    )

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
