"""Global configuration settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/quantpulse"
    redis_url: str = "redis://localhost:6379/0"

    # Services
    symbol_service_url: str = "http://localhost:8001"
    mdr_service_url: str = "http://localhost:8002"
    das_service_url: str = "http://localhost:8003"
    notifier_service_url: str = "http://localhost:8004"

    # External APIs
    yahoo_finance_timeout: int = 10
    yahoo_finance_retries: int = 3

    # Slack
    slack_webhook_url: Optional[str] = None
    slack_enabled: bool = False

    # Scheduler
    analyzer_schedule_time: str = "02:00"

    # Environment
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
