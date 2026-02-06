# QuantPulse - Setup & Getting Started

## What's Been Created

This is a **barebone v1.0 structure** of the QuantPulse market intelligence platform. All core components and infrastructure are in place, with TODO comments in the code indicating where implementation is needed.

### Structure Overview

```
QuantPulse/
├── backend/                    Python microservices backend
│   ├── services/               Four microservices
│   ├── shared/                 Common utilities and models
│   ├── requirements.txt        Python dependencies
│   └── Dockerfile              Service container image
├── frontend/                   React + TypeScript UI
│   ├── src/                    Application source
│   └── package.json            Node dependencies
├── docker-compose.yml          Local development orchestration
├── ARCHITECTURE.md             Detailed design documentation
├── README.md                   User-facing documentation
└── SETUP.md                    This file
```

## Quick Start

### 1. Start Services with Docker Compose

```bash
cd /home/darkshloser/PublicRepos/QuantPulse

# Build and start all services
docker-compose up -d

# Check services are healthy
docker-compose ps
```

Services will be available at:
- **Frontend:** http://localhost:3000
- **Symbol Management (SMS):** http://localhost:8001
- **Market Data Retriever (MDR):** http://localhost:8002
- **Data Analyzer (DAS):** http://localhost:8003
- **Notifier:** http://localhost:8004

### 2. Local Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start a service (in separate terminals)
python -m services.symbol_management.main  # Port 8001
python -m services.market_data.main         # Port 8002
python -m services.data_analyzer.main       # Port 8003
python -m services.notifier.main            # Port 8004
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev  # Runs on http://localhost:3000
```

## Key Files to Review

### Backend Services

1. **Symbol Management** → [backend/services/symbol_management/main.py](./backend/services/symbol_management/main.py)
   - TODO: Complete CRUD operations
   - TODO: Add validation

2. **Market Data Retriever** → [backend/services/market_data/main.py](./backend/services/market_data/main.py)
   - TODO: Implement Yahoo Finance provider
   - TODO: Implement idempotent writes
   - TODO: Add data caching

3. **Data Analyzer** → [backend/services/data_analyzer/main.py](./backend/services/data_analyzer/main.py)
   - TODO: Implement technical indicators (RSI, ATR, moving averages)
   - TODO: Implement signal generation logic
   - TODO: Add scheduler (APScheduler)

4. **Notifier** → [backend/services/notifier/main.py](./backend/services/notifier/main.py)
   - TODO: Implement Slack integration
   - TODO: Implement GUI notifications
   - TODO: Add scheduling logic

### Shared Code

- [backend/shared/models.py](./backend/shared/models.py) - Database models and API schemas
- [backend/shared/events.py](./backend/shared/events.py) - Event bus implementation
- [backend/shared/config.py](./backend/shared/config.py) - Configuration management
- [backend/shared/logging_config.py](./backend/shared/logging_config.py) - Structured logging

### Frontend

- [frontend/src/App.tsx](./frontend/src/App.tsx) - Main application component
- [frontend/src/components/SymbolList.tsx](./frontend/src/components/SymbolList.tsx) - Left panel
- [frontend/src/components/SignalPanel.tsx](./frontend/src/components/SignalPanel.tsx) - Main panel
- [frontend/src/api/client.ts](./frontend/src/api/client.ts) - API integration

## Design Principles to Follow

1. **User-driven universe** - Only calculate what users select
2. **Deterministic calculations** - Same input = same output
3. **Idempotent operations** - Safe to retry
4. **Loose coupling** - Event-driven communication
5. **Explainable signals** - Every alert includes "why"

## Next Steps for Implementation

### Phase 1: Core Data Pipeline
1. Implement Yahoo Finance provider (MDR service)
2. Implement technical indicators (RSI, ATR, MA)
3. Add APScheduler for daily analysis

### Phase 2: Notifications
1. Implement Slack integration
2. Add GUI real-time updates (WebSocket)
3. Add notification deduplication

### Phase 3: Advanced Features
1. User authentication
2. Custom indicator configuration
3. Backtesting framework
4. Additional data providers

## Testing the System

### Manual Testing

```bash
# Import symbols
curl -X POST http://localhost:8001/symbols/import \
  -H "Content-Type: application/json" \
  -d '[{
    "symbol":"AAPL",
    "yahoo_symbol":"AAPL",
    "instrument_type":"STOCK",
    "exchange":"NYSE",
    "currency":"USD"
  }]'

# Select a symbol
curl -X POST http://localhost:8001/symbols/select \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","selected":true}'

# Get selected symbols
curl http://localhost:8001/symbols/selected

# Run analysis
curl -X POST http://localhost:8003/analyze-all
```

### Logs

```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f symbol-management
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://quantpulse:quantpulse@localhost:5432/quantpulse

# Redis
REDIS_URL=redis://localhost:6379/0

# Slack (optional)
SLACK_WEBHOOK_URL=<your-webhook>
SLACK_ENABLED=false

# Scheduler
ANALYZER_SCHEDULE_TIME=02:00

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

## Database Management

```bash
# Connect to PostgreSQL
psql postgresql://quantpulse:quantpulse@localhost:5432/quantpulse

# View tables
\dt

# View data
SELECT * FROM symbols;
SELECT * FROM selected_symbols;
```

## Known Limitations (Barebone)

- [ ] No actual market data fetching (stub only)
- [ ] No indicator calculations
- [ ] No Slack integration
- [ ] No authentication
- [ ] No multi-user support
- [ ] No WebSocket real-time updates
- [ ] Limited error handling
- [ ] No database migrations (using SQLAlchemy create_all)

## Architecture Overview

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md)

Key concepts:
- **Microservices:** Decoupled services communicate via REST and Redis Events
- **Event Flow:** GUI → SMS → MDR → DAS → NS
- **Database Strategy:** One DB per service for loose coupling
- **Deterministic:** All calculations produce same output for same input

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# Check specific service logs
docker-compose logs symbol-management

# Verify ports are available
lsof -i :8001
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
psql postgresql://quantpulse:quantpulse@localhost:5432/quantpulse
```

### Frontend can't connect to API
```bash
# Check API URL in frontend/vite.config.ts
# Ensure backend services are running: docker-compose ps
# Check browser console for CORS issues
```

## Contributing

This is the foundation for QuantPulse. Implementation priorities:

1. **High Priority:**
   - Yahoo Finance data provider
   - Technical indicator implementations
   - Daily scheduler

2. **Medium Priority:**
   - Slack integration
   - GUI enhancements
   - Error handling

3. **Low Priority:**
   - Authentication
   - Advanced features
   - Kubernetes deployment

See individual service READMEs in `backend/services/*/` for specific TODOs.

## Resources

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [README.md](./README.md) - User documentation
- [backend/README.md](./backend/README.md) - Backend setup
- [frontend/README.md](./frontend/README.md) - Frontend setup

---

**Status:** Barebone v1.0 - Ready for feature implementation
**Git:** All changes committed to master
**Docker:** Ready to run `docker-compose up -d`
