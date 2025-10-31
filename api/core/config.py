from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):

    # loading envs
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API conigs 
    API_NAME:str = "Production Ready Medical LLM API"
    API_VERSION:str = "0.1.0"

    # Hugging Face
    HF_ENDPOINT: str ="https://u8hxw751s4q6eqhs.eu-west-1.aws.endpoints.huggingface.cloud"
    HF_TOKEN: str = os.getenv("HF_API_TOKEN", "")

    # HTTP client defaults
    httpx_timeout_seconds: int = int(os.getenv("HTTPX_TIMEOUT_SECONDS", "90"))
    retry_attempts: int = int(os.getenv("RETRY_ATTEMPTS", "3"))

    # Simple API key
    API_KEY: str | None = os.getenv("API_KEY")

settings = Settings()
