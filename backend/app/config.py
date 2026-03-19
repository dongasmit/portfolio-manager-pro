from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = ""

    # Kite Connect API
    kite_api_key: str = ""
    kite_api_secret: str = ""

    # Gemini
    gemini_api_key: str = ""

    # Groq
    groq_api_key: str = ""

    # App
    secret_key: str = "dev-secret-key"
    debug: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
