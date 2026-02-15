"""Global configuration settings."""

from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve .env relative to backend/ root (parent of shared/)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment / .env file."""

    # Database
    database_url: str
    redis_url: str

    # PostgreSQL (used by docker-compose variable substitution)
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""

    # Admin seed account
    admin_username: str
    admin_email: str
    admin_password: str

    # JWT Settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 30

    # Slack
    slack_webhook_url: str = ""
    slack_enabled: bool = False

    # Scheduler
    analyzer_schedule_time: str = "02:00"

    # SEC contact for User-Agent header
    sec_user_agent: str

    # NASDAQ Symbol Directory
    nasdaq_url: str = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
    nasdaq_timeout: int = 30
    nasdaq_retries: int = 3

    # Service URLs
    symbol_service_url: str = "http://localhost:8001"
    mdr_service_url: str = "http://localhost:8002"
    das_service_url: str = "http://localhost:8003"
    notifier_service_url: str = "http://localhost:8004"

    # Environment
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = str(_ENV_FILE)
        case_sensitive = False


settings = Settings()
