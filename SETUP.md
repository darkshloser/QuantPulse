# QuantPulse - Setup & Getting Started

## What's Been Implemented

QuantPulse now includes **complete authentication and authorization** with user management, role-based access control, and admin functionality. See [AUTHENTICATION.md](./AUTHENTICATION.md) for detailed information.

### Key Features Added
- ✅ User authentication (username/email + password)
- ✅ Secure password hashing (bcrypt)
- ✅ JWT token-based authorization
- ✅ Role-based access control (ADMIN, USER)
- ✅ User registration and approval workflow
- ✅ Admin profile and settings pages
- ✅ User management dashboard
- ✅ Symbol import restrictions (admin-only)
- ✅ Landing page for unauthenticated users

### New Services
- **Authentication Service** (Port 8000) - Handles login, registration, user management

### Updated Services
- **Symbol Management** - Protected endpoints for NASDAQ/symbol imports

## Quick Start

### 1. Local Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (now includes JWT, passlib, bcrypt)
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env to set JWT_SECRET_KEY
# IMPORTANT: Generate a secure random key in production

# Start services (in separate terminals)

# Terminal 1: Authentication Service (NEW)
cd services/auth
uvicorn main:app --reload --port 8000

# Terminal 2: Symbol Management Service
cd services/symbol_management
uvicorn main:app --reload --port 8001

# Terminal 3+: Other services (optional)
cd services/market_data
uvicorn main:app --reload --port 8002
```

#### Frontend

```bash
cd frontend

# Install dependencies (now includes react-router-dom)
npm install

# Create .env.local file
cat > .env.local << EOF
VITE_AUTH_API_URL=http://localhost:8000
VITE_SYMBOL_API_URL=http://localhost:8001
EOF

# Start dev server
npm run dev  # Runs on http://localhost:5173
```

### 2. Access the Application

1. **Landing Page** → http://localhost:5173/
2. **Login** → http://localhost:5173/login
3. **Register** → http://localhost:5173/register

### 3. Admin User (Pre-created)

Auto-created on first auth service startup:
- **Username:** `darkshloser`
- **Password:** `QT123456!_qt`
- **Access Level:** Full admin privileges

### 4. Start Services with Docker Compose (Optional)

```bash
cd /home/darkshloser/GitHub/Public/QuantPulse

# Build and start all services
docker-compose up -d

# Check services are healthy
docker-compose ps
```

Services will be available at:
- **Frontend:** http://localhost:3000 (or 5173 for Vite dev)
- **Authentication Service:** http://localhost:8000
- **Symbol Management (SMS):** http://localhost:8001
- **Market Data Retriever (MDR):** http://localhost:8002
- **Data Analyzer (DAS):** http://localhost:8003
- **Notifier:** http://localhost:8004

## Key Files to Review

### Authentication & Authorization (NEW)

1. **Authentication Service** → [backend/services/auth/main.py](./backend/services/auth/main.py)
   - User registration and login
   - JWT token generation and validation
   - Admin user management endpoints
   - User approval workflow

2. **Auth Utilities** → [backend/shared/auth.py](./backend/shared/auth.py)
   - Password hashing with bcrypt
   - JWT token creation/validation
   - FastAPI dependency injection for auth

3. **Updated Models** → [backend/shared/models.py](./backend/shared/models.py)
   - User model with role and approval status
   - UserRole and ApprovalStatus enums
   - Enhanced Pydantic schemas

4. **Frontend Auth Components** → [frontend/src/components/](./frontend/src/components/)
   - `Login.tsx` - User login page
   - `Register.tsx` - User registration page
   - `Landing.tsx` - Public landing page
   - `Profile.tsx` - Admin profile page
   - `Settings.tsx` - Admin settings and user management

5. **Auth Context** → [frontend/src/context/AuthContext.tsx](./frontend/src/context/AuthContext.tsx)
   - React Context for auth state management
   - useAuth hook for accessing auth info

6. **Route Protection** → [frontend/src/components/ProtectedRoute.tsx](./frontend/src/components/ProtectedRoute.tsx)
   - ProtectedRoute component (authentication required)
   - AdminRoute component (admin role required)
   - UnAuthenticatedRoute component (logged-out only)

7. **API Client** → [frontend/src/api/client.ts](./frontend/src/api/client.ts)
   - Enhanced with authentication endpoints
   - Automatic JWT token injection
   - Error handling for token expiration

### Backend Services

1. **Symbol Management** → [backend/services/symbol_management/main.py](./backend/services/symbol_management/main.py)
   - Updated import endpoints (admin-only)
   - Get symbols endpoint (public to authenticated users)

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

- [backend/shared/models.py](./backend/shared/models.py) - Database models and API schemas (now includes User model)
- [backend/shared/auth.py](./backend/shared/auth.py) - **NEW** Authentication utilities
- [backend/shared/events.py](./backend/shared/events.py) - Event bus implementation
- [backend/shared/config.py](./backend/shared/config.py) - Configuration management
- [backend/shared/logging_config.py](./backend/shared/logging_config.py) - Structured logging

### Frontend

- [frontend/src/App.tsx](./frontend/src/App.tsx) - Main application component with routing
- [frontend/src/context/AuthContext.tsx](./frontend/src/context/AuthContext.tsx) - **NEW** Authentication state
- [frontend/src/components/ProtectedRoute.tsx](./frontend/src/components/ProtectedRoute.tsx) - **NEW** Route guards
- [frontend/src/components/Login.tsx](./frontend/src/components/Login.tsx) - **NEW** Login page
- [frontend/src/components/Register.tsx](./frontend/src/components/Register.tsx) - **NEW** Registration page
- [frontend/src/components/Landing.tsx](./frontend/src/components/Landing.tsx) - **NEW** Public landing
- [frontend/src/components/Profile.tsx](./frontend/src/components/Profile.tsx) - **NEW** Admin profile
- [frontend/src/components/Settings.tsx](./frontend/src/components/Settings.tsx) - **NEW** Admin settings
- [frontend/src/components/SymbolList.tsx](./frontend/src/components/SymbolList.tsx) - Left panel
- [frontend/src/components/SignalPanel.tsx](./frontend/src/components/SignalPanel.tsx) - Main panel
- [frontend/src/api/client.ts](./frontend/src/api/client.ts) - API integration (now with auth)

## Authentication Features

For complete authentication documentation, see [AUTHENTICATION.md](./AUTHENTICATION.md)

### User Roles & Permissions

| Feature | ADMIN | USER | UNAUTHENTICATED |
|---------|:-----:|:----:|:-------:|
| Landing Page | ❌ | ❌ | ✅ |
| Login/Register | ✅ | ✅ | ❌ |
| Profile Page | ✅ | ❌ | ❌ |
| Settings Page | ✅ | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ |
| Symbol Import | ✅ | ❌ | ❌ |
| View Symbols | ✅ | ✅ | ❌ |
| Select Symbols | ✅ | ✅ | ❌ |

### Default Admin Account

```
Username: darkshloser
Password: QT123456!_qt
Email: admin@quantpulse.local (auto-generated)
```

Auto-created on first auth service startup.

## Design Principles to Follow

1. **User-driven universe** - Only calculate what users select
2. **Deterministic calculations** - Same input = same output
3. **Idempotent operations** - Safe to retry
4. **Loose coupling** - Event-driven communication
5. **Explainable signals** - Every alert includes "why"
6. **Secure authentication** - JWT tokens + bcrypt passwords

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

### Authentication Testing

1. **Admin Login**
   - Go to http://localhost:5173/login
   - Username: `darkshloser`
   - Password: `QT123456!_qt`
   - Should redirect to `/admin/dashboard`

2. **New User Registration**
   - Go to http://localhost:5173/register
   - Fill in username, email, password
   - Account created in PENDING status
   - Cannot login until approved by admin

3. **Admin Approval**
   - Login as admin
   - Go to `/admin/settings`
   - Click "Pending Approvals" tab
   - Review and approve/reject new users
   - Approved users can now login

4. **Symbol Management (Admin)**
   - Login as admin
   - Go to `/admin/settings` → "Symbol Management"
   - Click "Import NASDAQ Symbols"
   - Symbols are imported (admin-only endpoint)

### Manual API Testing

```bash
# Register new user
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "darkshloser",
    "password": "QT123456!_qt"
  }'

# Get current user (requires token)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/me

# List all users (admin only)
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  http://localhost:8000/admin/users

# Import NASDAQ symbols (admin only)
curl -X POST http://localhost:8001/symbols/import/nasdaq \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "NASDAQ_OFFICIAL",
    "instrumentType": "STOCK"
  }'
```

### Original Manual Testing

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

## Known Limitations (v1.0)

- [ ] Email verification on registration
- [ ] Password reset functionality
- [ ] Two-factor authentication
- [ ] Profile picture upload
- [ ] OAuth integration (GitHub, Google)
- [ ] Audit logging for admin actions
- [ ] Rate limiting on auth endpoints
- [ ] No actual market data fetching (stub only)
- [ ] No indicator calculations
- [ ] No Slack integration
- [ ] No multi-user workspace support
- [ ] No WebSocket real-time updates
- [ ] Limited error handling in data services

## What's Been Implemented

### Authentication & Authorization ✅
- [x] User registration
- [x] User login (username or email)
- [x] Secure password hashing (bcrypt)
- [x] JWT token-based authorization
- [x] Role-based access control (ADMIN, USER)
- [x] User approval workflow
- [x] Admin profile page
- [x] Admin settings page with user management
- [x] Symbol import restrictions (admin-only)
- [x] Landing page for unauthenticated users
- [x] Route protection and guards

### Remaining Features (TODO)
- [ ] Market data fetching from Yahoo Finance
- [ ] Technical indicator calculations
- [ ] Signal generation logic
- [ ] Slack notification integration
- [ ] Real-time WebSocket updates
- [ ] Backtesting framework

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
