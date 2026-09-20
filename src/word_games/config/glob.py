from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class _GlobalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="global_")

    pending_invitations_limit: PositiveInt = Field(
        default=10,
        description="Max number of pedning invitations sent by user.",
    )


GLOBAL_SETTINGS = _GlobalSettings()
