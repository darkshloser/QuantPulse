# QuantPulse Authentication & Authorization Implementation Guide

## Overview

This document describes the complete authentication and authorization system implementation for QuantPulse, fulfilling all requirements from the Authentication, Authorization & User Management specification.

## Backend Implementation

### 1. Database Models

**File**: `backend/shared/models.py`

Added the following models:

#### User Model
- `id`: Primary key (Integer)
- `username`: Unique username (String)
- `email`: Unique email address (String)
- `hashed_password`: Securely hashed password (String - bcrypt)
- `role`: User role enum (ADMIN or USER)
- `approval_status`: Account approval status (PENDING, APPROVED, REJECTED)
- `profile_picture_url`: Optional profile picture URL
- `first_name`, `last_name`: Optional personal information
- `is_active`: Account active status (Boolean)
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp

#### Supporting Enums
- `UserRole`: ADMIN, USER
- `ApprovalStatus`: PENDING, APPROVED, REJECTED

### 2. Authentication Service

**File**: `backend/services/auth/main.py`

Complete RESTful API for authentication:

#### Public Endpoints

```
POST /register
  Input: UserCreateRequest (username, email, password)
  Output: User object
  Description: Register new user (automatically sets role=USER, approval_status=PENDING)

POST /login
  Input: UserLoginRequest (username_or_email, password)
  Output: TokenResponse (access_token, refresh_token, user)
  Description: Authenticate user and return JWT tokens
  Validation: Checks approval status, account active status
```

#### Protected Endpoints

```
GET /me
  Auth: Required
  Output: User object
  Description: Get current user information

PUT /me/profile
  Auth: Required
  Input: ProfileUpdateRequest (first_name, last_name)
  Output: User object
  Description: Update user profile information
```

#### Admin-Only Endpoints

```
GET /admin/users
  Auth: Admin required
  Output: UserListResponse
  Description: List all users

GET /admin/users/pending
  Auth: Admin required
  Output: UserListResponse
  Description: List users awaiting approval

GET /admin/users/{user_id}
  Auth: Admin required
  Output: User object
  Description: Get specific user details

POST /admin/users/{user_id}/approve
  Auth: Admin required
  Output: Success message + User object
  Description: Approve pending user registration

POST /admin/users/{user_id}/reject
  Auth: Admin required
  Output: Success message + User object
  Description: Reject pending user registration

DELETE /admin/users/{user_id}
  Auth: Admin required
  Output: Success message
  Description: Deactivate user (soft delete)
```

### 3. Authentication Utilities

**File**: `backend/shared/auth.py`

Security functions:

- `hash_password(password)`: Hash password with bcrypt
- `verify_password(plain, hashed)`: Verify password against hash
- `create_access_token(user_id)`: Create JWT access token (default 24 hours)
- `create_refresh_token(user_id)`: Create JWT refresh token (default 30 days)
- `decode_token(token)`: Decode and validate JWT token
- `get_current_user()`: FastAPI dependency to extract authenticated user
- `get_admin_user()`: FastAPI dependency to require ADMIN role
- `get_approved_user()`: FastAPI dependency to require APPROVED status

**Configuration** (`backend/shared/config.py`):
- `jwt_secret_key`: Secret key for signing tokens (must be changed in production)
- `jwt_algorithm`: HS256
- `jwt_expiration_hours`: 24
- `jwt_refresh_expiration_days`: 30

### 4. Admin Protection for Symbol Service

**File**: `backend/services/symbol_management/main.py`

Updated endpoints with admin protection:

```
POST /symbols/import
  Auth: Admin required
  Input: List[SymbolSchema]
  Description: Import symbols from external source

POST /symbols/import/nasdaq
  Auth: Admin required
  Input: NasdaqImportRequest
  Description: Import NASDAQ symbols
```

### 5. Predefined Admin Account

On application startup, an automatic admin account is created:
- **Username**: `darkshloser`
- **Password**: `QT123456!_qt`
- **Role**: ADMIN
- **Approval Status**: APPROVED

This account is created only if it doesn't already exist.

## Frontend Implementation

### 1. Types and Models

**File**: `frontend/src/types.ts`

Added types:
- `User`: User account information
- `UserRole`: ADMIN, USER enum
- `ApprovalStatus`: PENDING, APPROVED, REJECTED enum
- `AuthToken`: JWT token response
- Updated `Symbol` interface with additional fields

### 2. API Client

**File**: `frontend/src/api/client.ts`

Enhanced with authentication:

#### Authentication API
- `authAPI.register(username, email, password)`: User registration
- `authAPI.login(username_or_email, password)`: User login
- `authAPI.logout()`: Clear stored tokens
- `authAPI.getCurrentUser()`: Get current user info
- `authAPI.updateProfile(firstName, lastName)`: Update profile
- `authAPI.listUsers()`: List all users (admin)
- `authAPI.getPendingUsers()`: List pending approvals (admin)
- `authAPI.getUserDetails(userId)`: Get user details (admin)
- `authAPI.approveUser(userId)`: Approve registration (admin)
- `authAPI.rejectUser(userId)`: Reject registration (admin)
- `authAPI.deleteUser(userId)`: Deactivate user (admin)

#### Token Management
- Automatic JWT token injection in request headers
- Token stored in localStorage
- Automatic logout on 401 (token expired)
- API interceptors for error handling

### 3. Authentication Context

**File**: `frontend/src/context/AuthContext.tsx`

React Context for managing authentication state:
- `user`: Current user object
- `isAuthenticated`: Boolean flag
- `isAdmin`: Check if user is admin
- `isLoading`: Loading state during init
- `logout()`: Clear auth state

### 4. Route Protection

**File**: `frontend/src/components/ProtectedRoute.tsx`

Route guard components:
- `ProtectedRoute`: Requires authentication
- `AdminRoute`: Requires admin role
- `UnAuthenticatedRoute`: Redirects to /app if logged in

### 5. Pages and Components

#### Landing Page (`frontend/src/components/Landing.tsx`)
- Description of QuantPulse
- Feature highlights
- Call-to-action buttons for login/register
- Getting started guide
- Accessible to unauthenticated users only

#### Login Page (`frontend/src/components/Login.tsx`)
- Username/email and password input
- Error handling and display
- Links to registration
- Redirect based on role (ADMIN → /admin/dashboard, USER → /app)

#### Register Page (`frontend/src/components/Register.tsx`)
- Username, email, password inputs
- Password confirmation
- Validation (password length, match)
- Success message with auto-redirect to login

#### Admin Profile Page (`frontend/src/components/Profile.tsx`)
- Display current user information
- Edit first name and last name
- Show role and approval status
- Display account creation and last login dates

#### Admin Settings Page (`frontend/src/components/Settings.tsx`)

Three tabs:

1. **Pending Approvals**
   - List of users awaiting approval
   - Approve/Reject buttons
   - User email, username, and registration date

2. **User Management**
   - Table of all users
   - Columns: username, email, role, status, registration date
   - Deactivate button for active users

3. **Symbol Management**
   - Import NASDAQ symbols button
   - Triggers admin-only endpoint
   - Shows success message with import summary

### 6. Application Layout

**File**: `frontend/src/App.tsx`

Updated with routing:

```
/                 → Landing page (unauthenticated)
/login            → Login page (unauthenticated)
/register         → Register page (unauthenticated)
/app              → Main dashboard (authenticated)
/admin/profile    → Admin profile (admin only)
/admin/settings   → Admin settings (admin only)
/admin/dashboard  → Admin dashboard (admin only)
```

Header includes:
- Welcome message with user name
- Navigation links (Profile, Settings for admins)
- Logout button

## Security Features

### 1. Password Security
- Passwords hashed with bcrypt (passlib)
- Passwords never stored in plain text
- Password validation on registration (minimum 8 characters)

### 2. JWT Tokens
- Access tokens: 24-hour expiration
- Refresh tokens: 30-day expiration
- Secure signing with HS256 algorithm
- Tokens stored in localStorage (frontend)
- Tokens included in Authorization header

### 3. Role-Based Access Control
- ADMIN role required for:
  - Accessing admin pages
  - Approving/rejecting users
  - Deleting users
  - Importing symbols
  - User management
- USER role has access to:
  - Main application dashboard
  - Symbol selection
  - Signal viewing

### 4. Account Approval Workflow
- New users created in PENDING status
- Cannot login until APPROVED by admin
- Admin can approve or reject registrations
- Users can be deactivated but not deleted

## Configuration

### Backend Environment Variables

Add to `.env` file:

```
JWT_SECRET_KEY=your-very-secure-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=30
```

### Frontend Environment Variables

Add to `.env.local`:

```
VITE_AUTH_API_URL=http://localhost:8000
VITE_SYMBOL_API_URL=http://localhost:8001
```

## Installation & Setup

### Backend

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Create database tables:
```bash
python -c "from shared.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

3. Start auth service:
```bash
cd backend/services/auth
uvicorn main:app --reload --port 8000
```

4. Start symbol service (with admin protection):
```bash
cd backend/services/symbol_management
uvicorn main:app --reload --port 8001
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start dev server:
```bash
npm run dev
```

## Testing

### Admin User Login
- **Username**: darkshloser
- **Email**: admin@quantpulse.local (auto-created)
- **Password**: QT123456!_qt

### User Registration Flow
1. Go to `/register`
2. Create new account with email and password
3. Account created in PENDING status
4. Admin approves via Settings → Pending Approvals
5. User can now login and access `/app`

## Requirements Coverage

| Requirement | Implementation |
|------------|-----------------|
| AR-1: Username/email + password auth | Login endpoint with both username and email support |
| AR-1: Secure password hashing | bcrypt via passlib |
| AR-1: Auth required for internal pages | ProtectedRoute components |
| AR-2: Predefined admin account | Auto-created on startup |
| AR-3: Role-based authorization | UserRole enum (ADMIN, USER) |
| AR-4: Admin profile page | /admin/profile with editing |
| AR-5: Admin settings page | /admin/settings with 3 tabs |
| Symbol import endpoints restricted | @get_admin_user dependency |
| SR-1: Active symbols visible | SymbolList component |
| PR-1: Unauthenticated landing page | / route with landing component |
| UR-1: User registration | /register endpoint |
| UR-2: Admin approval workflow | Pending approvals tab in settings |
| UR-3: Post-approval access | Login check for APPROVED status |
| UR-4: Symbol selection | Double-click functionality |
| UR-5: Selected symbols persistence | SelectedSymbol model |

## Future Enhancements

1. **Password Reset**: Email-based password reset flow
2. **2FA**: Two-factor authentication
3. **OAuth**: GitHub, Google authentication
4. **Audit Log**: Track admin actions
5. **Rate Limiting**: Prevent brute force attacks
6. **Session Management**: Multiple device support
7. **Profile Picture Upload**: Handle image uploads
8. **Email Verification**: Email verification on registration
9. **Refresh Token Rotation**: Rotate refresh tokens on use
10. **Role Hierarchy**: More granular roles (MODERATOR, etc.)
