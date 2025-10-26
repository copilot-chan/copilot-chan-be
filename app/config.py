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

settings = Settings()
