"""Global configuration settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/quantpulse"
    redis_url: str = "redis://localhost:6379/0"

    # JWT Settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 30


    # Scheduler
    analyzer_schedule_time: str = "02:00"

    # NASDAQ Symbol Directory
    nasdaq_url: str = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
    nasdaq_timeout: int = 30
    nasdaq_retries: int = 3

    # Environment
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
