# QuantPulse

A modular, microservice-based market intelligence platform for detecting financial signals based on technical indicators.

⚠️ **Disclaimer:** This platform is for informational purposes only. It is not financial advice and should not be used as the sole basis for investment decisions.

## Overview

QuantPulse helps you:
- **Monitor** a controlled universe of financial instruments (stocks, metals, etc.)
- **Analyze** historical market data with technical indicators
- **Detect** symbols that meet your defined criteria
- **Get Notified** via Slack and a web GUI when signals trigger

The platform is **signal-based, not advisory**—it focuses on probability, volatility, and pattern detection.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.11+ (for backend development)

### Start Everything

```bash
# Build and start all services
docker-compose up -d

# Services will be available at:
# - Frontend: http://localhost:3000
# - Symbol Service: http://localhost:8001
# - Market Data Service: http://localhost:8002
# - Analyzer Service: http://localhost:8003
# - Notifier Service: http://localhost:8004
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Setup

1. **Import symbols** (currently manual via API):
   ```bash
   curl -X POST http://localhost:8001/symbols/import \
     -H "Content-Type: application/json" \
     -d '[{"symbol":"AAPL","yahoo_symbol":"AAPL","instrument_type":"STOCK","exchange":"NYSE","currency":"USD"}]'
   ```

2. **Select symbols** via the GUI or API:
   - Go to http://localhost:3000
   - Search for and select symbols
   - Selection triggers automatic data fetching

3. **Run analysis** manually or let the daily scheduler (02:00 CET) handle it:
   ```bash
   curl -X POST http://localhost:8003/analyze-all
   ```

4. **View signals** in the GUI or check API:
   ```bash
   curl http://localhost:8004/notifications
   ```

## Architecture

QuantPulse follows a **microservice architecture** with event-driven communication:

- **Symbol Management Service** - Master symbol registry
- **Market Data Retriever** - Historical OHLCV data fetching
- **Data Analyzer** - Technical indicator evaluation
- **Notifier** - Alert delivery via Slack & GUI
- **Frontend GUI** - React-based symbol selection and monitoring

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed design documentation.

## Project Structure

```
quantpulse/
├── backend/                          # Python backend services
│   ├── services/
│   │   ├── symbol_management/        # SMS service
│   │   ├── market_data/              # MDR service
│   │   ├── data_analyzer/            # DAS service
│   │   └── notifier/                 # NS service
│   ├── shared/
│   │   ├── config.py                 # Settings
│   │   ├── database.py               # DB connection
│   │   ├── models.py                 # SQLAlchemy models & Pydantic schemas
│   │   ├── events.py                 # Event bus (Redis Streams)
│   │   └── logging_config.py         # Structured logging
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/                         # React/TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── SymbolList.tsx        # Left panel: symbol search
│   │   │   └── SignalPanel.tsx       # Main panel: signals
│   │   ├── api/
│   │   │   └── client.ts             # API client
│   │   ├── types.ts                  # TypeScript types
│   │   ├── App.tsx                   # Main component
│   │   └── main.tsx                  # Entry point
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docker-compose.yml
├── ARCHITECTURE.md
└── README.md
```

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run a service
python -m services.symbol_management.main
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Configuration

### Environment Variables

See [backend/.env.example](./backend/.env.example) for all options:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/quantpulse
REDIS_URL=redis://localhost:6379/0

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_ENABLED=true

# Scheduler
ANALYZER_SCHEDULE_TIME=02:00  # Daily analysis time (CET)

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

## API Endpoints

### Symbol Management Service (Port 8001)
```
GET    /symbols                      # List all symbols
GET    /symbols/selected             # List selected symbols
POST   /symbols/select               # Select/deselect symbol
POST   /symbols/import               # Import symbols (admin)
```

### Market Data Service (Port 8002)
```
GET    /market-data/{symbol}         # Historical data
POST   /fetch/{symbol}               # Manual fetch
POST   /fetch-all                    # Fetch all selected
```

### Analyzer Service (Port 8003)
```
GET    /signals/{symbol}             # Recent signals
POST   /analyze/{symbol}             # Analyze single symbol
POST   /analyze-all                  # Daily analysis
```

### Notifier Service (Port 8004)
```
GET    /notifications                # Recent notifications
POST   /notify/slack/{signal_id}     # Send Slack alert
POST   /notify/gui/{signal_id}       # Send GUI alert
```

## Design Principles

1. **User-driven universe** - Only analyze symbols users select
2. **Deterministic calculations** - Same input always produces same output
3. **Idempotent operations** - Safe to retry without side effects
4. **Loose coupling** - Services communicate via events
5. **Replaceable providers** - Data providers abstracted behind interfaces
6. **Explainable signals** - Every alert explains why it triggered

## Security Considerations

- API keys are stored in environment variables (never in code)
- Input validation on all endpoints
- SQL injection prevention via ORM
- Rate limiting recommended for production
- No sensitive data in logs
- Tokens and secrets require secure storage (future)

## Monitoring & Observability

- **Logging:** JSON-structured logs for easy parsing
- **Metrics:** Job duration, symbols processed, error rates
- **Health checks:** Docker health checks on all services
- **Error tracking:** Failures logged separately from signals

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Roadmap

- [ ] User authentication & multi-tenant support
- [ ] Custom indicator configuration UI
- [ ] Backtesting framework
- [ ] More data providers
- [ ] Email notifications
- [ ] Kubernetes deployment
- [ ] Admin dashboard
- [ ] WebSocket real-time updates

## Troubleshooting

### Services Won't Start
- Check Docker is running
- Verify ports 5432, 6379, 3000, 8001-8004 are available
- Check logs: `docker-compose logs <service-name>`

### No Data Appearing
- Ensure symbols are imported
- Select symbols in the GUI
- Check market data fetching: `POST /fetch-all`
- View logs for errors

### Slack Notifications Not Working
- Set `SLACK_WEBHOOK_URL` and `SLACK_ENABLED=true`
- Check notifier service logs
- Verify webhook URL is valid

## Contributing

This is the barebone v1.0 structure. Areas for implementation:

1. **Yahoo Finance provider** - Implement data fetching
2. **Technical indicators** - RSI, ATR, moving averages, etc.
3. **Signal generation logic** - Trigger criteria evaluation
4. **Slack integration** - Message formatting and delivery
5. **Frontend state management** - Global state for symbols/signals
6. **Tests** - Unit and integration tests

## License

[Add your license here]

## Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Check [ARCHITECTURE.md](./ARCHITECTURE.md) for design details
- Review service READMEs in each `backend/services/*/` directory
