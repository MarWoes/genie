"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API and TensorX model client."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    tensorx_api_key: str | None = None
    tensorx_base_url: str = "https://api.tensorx.ai/v1"
    tensorx_model: str = "z-ai/glm-5.3-flash"


settings = Settings()
