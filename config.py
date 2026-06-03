from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from .env.mongodb.
    """

    model_config = SettingsConfigDict(env_file=".env.mongodb")
    mongodb_uri: str
    mongodb_db_name: str


settings = Settings()  # type: ignore[call-arg]
