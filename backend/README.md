# QuantPulse Backend

Microservice-based market intelligence platform backend.

## Architecture

### Services

1. **Symbol Management Service (SMS)** - Port 8001
   - Manages financial instruments universe
   - Stores user-selected symbols
   - No market data, no calculations

2. **Market Data Retriever Service (MDR)** - Port 8002
   - Fetches and maintains historical price data
   - Idempotent writes
   - Interfaces with Yahoo Finance

3. **Data Analyzer Service (DAS)** - Port 8003
   - Applies technical indicators
   - Evaluates trigger criteria
   - Deterministic, stateless execution

4. **Notifier Service (NS)** - Port 8004
   - Sends alerts via Slack and GUI
   - Manages notification scheduling

### Common

- `shared/`: Shared utilities, models, and database setup
- `events/`: Event definitions and event bus implementation

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
alembic upgrade head

# Start a service
python -m services.symbol_management.main
```

## Event Flow

```
GUI → SMS (SYMBOLS_SELECTED)
  ↓
MDR (MARKET_DATA_UPDATED)
  ↓
DAS (SIGNAL_TRIGGERED)
  ↓
NS (Slack + GUI notification)
```

## Data Storage

- PostgreSQL for all services
- Redis for caching and event streaming
- Event-driven communication between services
