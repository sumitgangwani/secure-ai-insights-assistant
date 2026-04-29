from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    database_url: str = "sqlite:///./data/insights.db"
    max_query_rows: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
