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
    HF_ENDPOINT: str = os.getenv("HF_ENDPOINT_URL", "")
    HF_TOKEN: str = os.getenv("HF_API_TOKEN", "")

    # Simple API key
    API_KEY: str = os.getenv("API_KEY")

settings = Settings()
