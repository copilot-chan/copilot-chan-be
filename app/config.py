# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )
    
    APP_NAME: str = "copilot-chan"
    DB_URL: str = "sqlite:///./my_agent_data.db"
    IS_DEV: bool = False
    LOCAL_AGENT_PORT: int = 8001
    CLIENT_PORT: int = 8000
    WEBHOOK_HOST: str | None = None
    MEM0_PROJECT_ID: str | None = None
    MEM0_WEBHOOK_SECRET: str | None = None

settings = Settings()
