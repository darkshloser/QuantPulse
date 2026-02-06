# QuantPulse Architecture

## High-Level Overview

QuantPulse is a modular, microservice-based market intelligence platform that:
- Maintains a controlled universe of financial instruments
- Retrieves and stores historical market data
- Applies technical and custom analytical indicators
- Detects symbols that meet user-defined criteria
- Notifies users via Slack and GUI

The platform is **signal-based, not advisory**, focusing on probability, volatility, and pattern detection.

## Core Design Principles

1. **User-driven symbol universe** - Nothing is calculated unless the user selected it
2. **Deterministic & reproducible calculations** - Same input always produces same output
3. **Idempotent data ingestion** - Safe to retry operations without side effects
4. **Loose coupling between services** - Event-driven communication
5. **Replaceable data providers** - Yahoo Finance abstracted behind provider interface
6. **Explainable signals** - Every signal includes why it was triggered

## Microservice Architecture

### 1. Symbol Management Service (SMS) - Port 8001
**Responsibility:** Acts as source of truth for all supported instruments

**Data Model:**
- Symbol (internal identifier)
- Yahoo symbol
- Instrument type (STOCK, METAL)
- Exchange
- Currency
- Active/inactive status

**Capabilities:**
- Maintain master symbol registry
- Expose symbol list to GUI
- Track user-selected symbols
- Emit `SYMBOLS_SELECTED` events

**Key Rules:**
- No market data stored
- No calculations
- No Yahoo Finance calls

**Endpoints:**
```
GET /symbols                    # All available symbols
POST /symbols/select            # Select/deselect symbol
GET /symbols/selected           # User's selected symbols
POST /symbols/import (admin)    # Bulk import symbols
```

### 2. Market Data Retriever Service (MDR) - Port 8002
**Responsibility:** Fetch and maintain historical price & volume data

**Data Model:**
- Symbol
- Date
- OHLCV (Open, High, Low, Close, Volume)

**Behavior:**
- Fetch last 90 days for newly selected symbols
- Incrementally fetch missing days only
- Update data only for user-selected symbols
- Idempotent writes (safe to retry)

**Scheduling:**
- Periodic job (hourly or daily)
- Manual trigger via event when selection changes

**Data Source:**
- Yahoo Finance (abstracted behind provider interface)

**Endpoints:**
```
GET /market-data/{symbol}       # Historical data
POST /fetch/{symbol}            # Manual fetch
POST /fetch-all                 # Fetch all selected
```

**Events:**
- Consumes: `SYMBOLS_SELECTED`
- Publishes: `MARKET_DATA_UPDATED`

### 3. Data Analyzer Service (DAS) - Port 8003
**Responsibility:** Apply indicators and evaluate trigger criteria

**Capabilities:**
- RSI thresholds
- ATR expansion
- Moving average crossovers
- Custom volatility models
- User-defined indicator combinations

**Behavior:**
- Daily scheduler at 02:00 CET
- Only processes user-selected symbols
- Deterministic (same input → same output)
- Stateless execution (results persisted)
- No data fetching

**Output:**
- Signal results per symbol
- Explanation payload (which indicators passed)
- Confidence score (0.0-1.0)

**Endpoints:**
```
GET /signals/{symbol}           # Recent signals
POST /analyze/{symbol}          # Analyze single symbol
POST /analyze-all               # Daily analysis
```

**Events:**
- Consumes: `MARKET_DATA_UPDATED`
- Publishes: `SIGNAL_TRIGGERED`

### 4. Notifier Service (NS) - Port 8004
**Responsibility:** Deliver results to external systems and UI

**Channels:**
- Slack (primary)
- GUI notifications

**Behavior:**
- Send alerts only on working days
- One alert per symbol per run (no spam)
- Include explanation & confidence
- Include Yahoo Finance link

**Message Content:**
- Symbol
- Signal type
- Indicator summary
- Timestamp
- Yahoo link

**Endpoints:**
```
GET /notifications              # Recent notifications
POST /notify/slack/{signal_id}  # Send Slack alert
POST /notify/gui/{signal_id}    # Send GUI alert
```

**Events:**
- Consumes: `SIGNAL_TRIGGERED`

## Communication Patterns

### Synchronous (REST)
**Use when:** GUI requests data, CRUD operations
**Technology:** REST over HTTP, FastAPI

### Asynchronous (Event-driven)
**Use when:** State changes propagate, avoiding tight coupling
**Technology:** Redis Streams

### Event Flow

```
GUI → SMS (SYMBOLS_SELECTED)
     ↓
    MDR (MARKET_DATA_UPDATED)
     ↓
    DAS (SIGNAL_TRIGGERED)
     ↓
    NS (Slack + GUI notification)
```

## Data Storage Strategy

### Databases per Service
- **Symbol Service:** PostgreSQL (symbol registry, user selections)
- **Market Data:** PostgreSQL (timeseries tables with date indexes)
- **Analyzer:** PostgreSQL (results, history, signals)
- **Notifier:** Uses other services' data (read-only)

### Why Not Shared Database?
- Prevents tight coupling
- Enables independent scaling
- Cleaner ownership
- Easier to migrate services

### Cache Strategy
- Redis for event streaming
- Redis for frequency data caching (optional)
- Session/token management (future)

## Technology Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL
- **Cache/Events:** Redis
- **Job Scheduling:** APScheduler
- **Task Queue:** Celery (optional for heavy processing)

### Frontend
- **Framework:** React 18
- **Language:** TypeScript
- **Bundler:** Vite
- **HTTP Client:** Axios
- **Styling:** CSS (minimal framework approach)

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose (initial), Kubernetes (future)
- **Monitoring:** Structured JSON logging (initial)

## Non-Functional Requirements

### Reliability
- Retry logic for data fetching (exponential backoff)
- Graceful degradation if Yahoo Finance is down
- Circuit breaker pattern for external API calls
- Duplicate detection for idempotent operations

### Observability
- Structured JSON logging for all services
- Metrics: job duration, symbols processed, error rates
- Alert failures are separate from trading signals
- Audit trail for signal generation

### Security
- API authentication (JWT tokens, future)
- Rate limiting on public endpoints
- No exposed Yahoo credentials (use environment variables)
- Input validation on all endpoints
- SQL injection prevention via ORM

### Compliance
- No buy/sell wording in alerts
- Clear disclaimer: "Informational only, not financial advice"
- Disclaimer in GUI footer and Slack messages
- No personalized recommendations
- Signal explanations must be explicit

## Deployment Architecture

### Development
```
docker-compose up
```

### Production (Future)
- Kubernetes cluster
- Separate PostgreSQL with replication
- Redis Sentinel for high availability
- Load balancing for services
- CI/CD pipeline
- Monitoring and alerting

## Scaling Considerations

1. **Database:** Separate instances per service, replication for reliability
2. **Cache:** Redis Sentinel for HA, distributed cache if needed
3. **Services:** Horizontal scaling with load balancing
4. **Batch Processing:** Celery workers for heavy analysis tasks
5. **Event System:** Kafka if throughput exceeds Redis Streams capacity

## Future Enhancements

- [ ] User authentication and multi-tenant support
- [ ] Custom indicator configuration UI
- [ ] Backtesting framework
- [ ] Alert scheduling and quiet hours
- [ ] Email notifications
- [ ] REST API token management
- [ ] Admin dashboard
- [ ] More data providers (Alpha Vantage, IEX, etc.)
