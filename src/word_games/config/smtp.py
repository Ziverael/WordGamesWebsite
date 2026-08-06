from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _SMTPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SMTP_")

    server: str = Field(min_length=1, serialization_alias="MAIL_SERVER")
    port: int = Field(serialization_alias="MAIL_PORT")
    use_tls: bool = Field(default=False, serialization_alias="MAIL_USE_TLS")
    use_ssl: bool = Field(default=False, serialization_alias="MAIL_USE_SSL")
    username: str | None = Field(
        default=None, serialization_alias="MAIL_USERNAME"
    )
    password: str | None = Field(
        default=None, serialization_alias="MAIL_PASSWORD"
    )
    default_sender: str = Field(
        default="word games",
        min_length=1,
        serialization_alias="MAIL_DEFAULT_SENDER",
    )


SMTP_SETTINGS = _SMTPSettings()
