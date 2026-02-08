"""Event definitions and event bus implementation."""

from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum
import json
import redis

from shared.config import settings


class EventType(str, Enum):
    """Event types in the system."""
    SYMBOLS_SELECTED = "symbols_selected"
    SYMBOLS_IMPORTED = "symbols_imported"
    MARKET_DATA_UPDATED = "market_data_updated"
    SIGNAL_TRIGGERED = "signal_triggered"
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"


class Event:
    """Base event class."""

    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class EventBus:
    """Redis-based event bus for inter-service communication."""

    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.channel_prefix = "quantpulse:events:"

    def publish(self, event: Event) -> None:
        """Publish an event to Redis Streams."""
        channel = f"{self.channel_prefix}{event.event_type.value}"
        self.redis_client.xadd(channel, {"data": event.to_json()})

    def subscribe(self, event_type: EventType, callback) -> None:
        """Subscribe to events (simplified - use worker in production)."""
        channel = f"{self.channel_prefix}{event_type.value}"
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    callback(data)
                except json.JSONDecodeError:
                    pass

    def get_recent_events(self, event_type: EventType, count: int = 10) -> list:
        """Get recent events of a type."""
        channel = f"{self.channel_prefix}{event_type.value}"
        events = self.redis_client.xrevrange(channel, count=count)
        return [json.loads(event[1][b"data"]) for event in events]


# Global event bus instance
event_bus = EventBus()
