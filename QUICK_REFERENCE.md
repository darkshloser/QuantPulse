# QuantPulse Authentication - Quick Reference

## 🚀 Quick Start (30 seconds)

### 1. Start Backend Services (3 terminals)

```bash
# Terminal 1: Auth Service
cd backend/services/auth
pip install -r requirements.txt  # First time only
uvicorn main:app --reload --port 8000

# Terminal 2: Symbol Service  
cd backend/services/symbol_management
uvicorn main:app --reload --port 8001

# Terminal 3: Frontend
cd frontend
npm install  # First time only
npm run dev
```

### 2. Access Application
- **Frontend**: http://localhost:5173/
- **Auth API**: http://localhost:8000
- **Symbol API**: http://localhost:8001

### 3. Admin Login
- **Username**: `darkshloser`
- **Password**: `QT123456!_qt`

## 📍 Routes

| Route | Role | Purpose |
|-------|------|---------|
| `/` | Public | Landing page |
| `/login` | Public | User login |
| `/register` | Public | User registration |
| `/app` | Authenticated | Main dashboard |
| `/admin/profile` | Admin | Profile & settings |
| `/admin/settings` | Admin | User management |

## 👤 User Roles

### ADMIN
- ✅ Full system access
- ✅ Manage users (approve, reject, delete)
- ✅ Import symbols (NASDAQ)
- ✅ View all users
- ✅ Admin dashboard

### USER
- ✅ View active symbols
- ✅ Select symbols
- ✅ View signals
- ❌ Cannot manage users
- ❌ Cannot import symbols

### UNAUTHENTICATED
- ✅ View landing page
- ✅ Login
- ✅ Register
- ❌ Cannot access dashboard
- ❌ Cannot view symbols

## 🔐 Authentication

### Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "darkshloser",
    "password": "QT123456!_qt"
  }'
```

### Use Token
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/me
```

## 📝 User Workflow

1. **Register** → `POST /register`
   - Status: PENDING
   - Cannot login yet
   
2. **Admin Approves** → `POST /admin/users/{id}/approve`
   - Status: APPROVED
   - Can now login
   
3. **User Logins** → `POST /login`
   - Gets JWT tokens
   - Stored in localStorage
   - Included in all requests

4. **User Accesses App** → `/app`
   - Sees symbols
   - Can select symbols
   - Can view signals

## 🛠️ Admin Tasks

### Manage Users
- Go to `/admin/settings`
- Tab: "User Management"
- Table shows all users
- Deactivate users with button

### Approve New Users
- Go to `/admin/settings`
- Tab: "Pending Approvals"
- Review user details
- Click Approve/Reject

### Import Symbols
- Go to `/admin/settings`
- Tab: "Symbol Management"
- Click "Import NASDAQ Symbols"
- Symbols imported automatically

### Edit Profile
- Go to `/admin/profile`
- Edit first/last name
- Click Save

## 📊 API Endpoints

### Authentication Service (Port 8000)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/register` | - | Register user |
| POST | `/login` | - | Get JWT token |
| GET | `/me` | ✅ | Get user info |
| PUT | `/me/profile` | ✅ | Update profile |
| GET | `/admin/users` | 👑 | List all users |
| GET | `/admin/users/pending` | 👑 | List pending users |
| POST | `/admin/users/{id}/approve` | 👑 | Approve user |
| POST | `/admin/users/{id}/reject` | 👑 | Reject user |
| DELETE | `/admin/users/{id}` | 👑 | Deactivate user |

### Symbol Service (Port 8001)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/symbols` | ✅ | List active symbols |
| POST | `/symbols/select` | ✅ | Select symbol |
| POST | `/symbols/import` | 👑 | Import symbols |
| POST | `/symbols/import/nasdaq` | 👑 | Import NASDAQ |

Legend: `-` = Public, `✅` = Authenticated, `👑` = Admin only

## 🔑 Default Credentials

```
Admin Account (Auto-created on startup):
├─ Username: darkshloser
├─ Password: QT123456!_qt
├─ Email: admin@quantpulse.local
└─ Role: ADMIN (Approved)
```

## 📝 Environment Variables

### Backend (.env)
```env
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=30
DATABASE_URL=postgresql://user:password@localhost:5432/quantpulse
```

### Frontend (.env.local)
```env
VITE_AUTH_API_URL=http://localhost:8000
VITE_SYMBOL_API_URL=http://localhost:8001
```

## 🧪 Testing Scenarios

### Scenario 1: Admin Login
```bash
1. Visit http://localhost:5173/login
2. Username: darkshloser
3. Password: QT123456!_qt
4. → /admin/dashboard
```

### Scenario 2: Register & Approve
```bash
1. Visit http://localhost:5173/register
2. Enter username, email, password
3. Redirect to login
4. Admin login
5. Go to /admin/settings
6. Click "Pending Approvals"
7. Click "Approve"
8. New user can now login
```

### Scenario 3: Import Symbols
```bash
1. Admin login
2. Go to /admin/settings
3. Click "Symbol Management" tab
4. Click "Import NASDAQ Symbols"
5. Symbols imported
6. Go to /app
7. Symbols visible in left panel
```

## ⚙️ Configuration

### Password Requirements
- Minimum 8 characters
- Any special characters allowed
- Case-sensitive

### Token Expiration
- **Access Token**: 24 hours
- **Refresh Token**: 30 days

### JWT Algorithm
- Algorithm: HS256
- Secret: Configurable (production: generate new)

## 🐛 Troubleshooting

### "Invalid credentials" on login
- Check username/email spelling
- Check password (case-sensitive)
- Verify user is APPROVED status
- Verify user is_active = true

### "User not approved" on login
- User was just registered
- Go to admin settings
- Approve user in "Pending Approvals"

### Token expired
- Automatic logout happens
- Redirect to /login
- Login again to get new token

### CORS errors in browser
- Check .env.local VITE_* URLs
- Verify backend services running
- Check ports: 8000, 8001

### Services won't start
- Check ports are available
- Check Python/Node installed
- Check dependencies installed (pip/npm install)

## 📚 Full Documentation

- **Complete Guide**: [AUTHENTICATION.md](./AUTHENTICATION.md)
- **Implementation Summary**: [AUTH_IMPLEMENTATION_SUMMARY.md](./AUTH_IMPLEMENTATION_SUMMARY.md)
- **Checklist**: [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)
- **Setup Guide**: [SETUP.md](./SETUP.md)

## 🎯 Key Files

### Backend
- `backend/services/auth/main.py` - Auth service
- `backend/shared/auth.py` - Security utilities
- `backend/shared/models.py` - Database models

### Frontend
- `frontend/src/App.tsx` - Routing & layout
- `frontend/src/context/AuthContext.tsx` - State management
- `frontend/src/components/Login.tsx` - Login page
- `frontend/src/components/Register.tsx` - Register page
- `frontend/src/api/client.ts` - API calls

## ✅ Status

- **Backend**: ✅ Complete
- **Frontend**: ✅ Complete
- **Documentation**: ✅ Complete
- **Security**: ✅ Implemented
- **Testing**: ✅ Ready

---

**Last Updated**: February 8, 2026
**Version**: 1.0
**Support**: See documentation files for details
