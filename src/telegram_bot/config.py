from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_token: str = Field()

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_BOT_")


settings = Settings()
