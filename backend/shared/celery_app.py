"""Celery application configuration with scheduled beat tasks."""

from celery import Celery
from celery.schedules import crontab

from shared.config import settings

# Use dedicated Redis DB for Celery broker (separate from events on DB 0)
broker_url = settings.celery_broker_url or settings.redis_url

celery_app = Celery(
    "quantpulse",
    broker=broker_url,
    backend=broker_url,
    include=["services.data_analyzer.tasks"],
)

celery_app.conf.update(
    timezone="Europe/Berlin",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    beat_schedule={
        "evaluate-signals-evening": {
            "task": "services.data_analyzer.tasks.evaluate_all_signals",
            "schedule": crontab(hour=18, minute=0, day_of_week="mon-fri"),
        },
        "evaluate-signals-night": {
            "task": "services.data_analyzer.tasks.evaluate_all_signals",
            "schedule": crontab(hour=22, minute=0, day_of_week="mon-fri"),
        },
    },
)
