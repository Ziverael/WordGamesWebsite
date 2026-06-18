from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_")

    SECRET_KEY: str = Field(min_length=1)
    SQLALCHEMY_DATABASE_URI: str = Field(min_length=1)


APP_SETTINGS = _AppSettings()
