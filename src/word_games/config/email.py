from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="email_")

    default_sender: str = Field(default="word games", min_length=1)


SMTP_SETTINGS = _EmailSettings()
