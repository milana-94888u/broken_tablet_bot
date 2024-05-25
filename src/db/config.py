from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    file_path: str
    echo: bool = False

    model_config = SettingsConfigDict(env_prefix="SQL_")

    @cached_property
    def url(self) -> str:
        return f"sqlite+aiosqlite:///{self.file_path}"


settings = Settings()
