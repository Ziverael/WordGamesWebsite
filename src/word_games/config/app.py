from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppSettings(BaseSettings):
    """Those settings are directly mapped to Flask app configs
    therefore they must comply with very specific naming conventions.
    """

    model_config = SettingsConfigDict(
        env_prefix="app_", env_nested_delimiter="__"
    )

    database_connection_string: str = Field(
        min_length=1,
        alias="DATABASE_CONNECTION_STRING",
        serialization_alias="SQLALCHEMY_DATABASE_URI",
    )
    secret_key: str = Field(
        min_length=1,
        serialization_alias="SECRET_KEY",
    )
    debug: bool = Field(
        default=False,
        serialization_alias="DEBUG",
    )
    env: Literal["dev", "pre", "pro"]


APP_SETTINGS = _AppSettings()
