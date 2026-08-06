from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class _DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_")

    pool_size: PositiveInt = 10
    max_overflow: PositiveInt = 20
    connection_string: str = Field(min_length=1)


DATABASE_SETTINGS = _DatabaseSettings()
