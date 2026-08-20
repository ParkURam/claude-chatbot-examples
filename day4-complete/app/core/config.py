# app/core/config.py
from anthropic import Anthropic
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str = "sqlite:///./chat.db"

    class Config:
        env_file = ".env"


settings = Settings()


def get_claude_client() -> Anthropic:
    return Anthropic(api_key=settings.anthropic_api_key)
