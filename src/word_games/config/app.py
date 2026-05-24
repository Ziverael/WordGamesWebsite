from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="app_")

    secret_key: str = Field(min_length=1)


APP_SETTINGS = _AppSettings()
