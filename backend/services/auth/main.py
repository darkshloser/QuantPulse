"""Authentication Service - handles user login, registration, and token management."""

import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from shared.config import settings
from shared.database import get_db, engine, Base
from shared.models import (
    User,
    UserRole,
    ApprovalStatus,
    UserCreateRequest,
    UserLoginRequest,
    TokenResponse,
    UserSchema,
    UserListResponse,
    UserApprovalRequest,
    ProfileUpdateRequest,
)
from shared.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_admin_user,
    get_approved_user,
)
from shared.logging_config import logger as app_logger

# Create tables (safe to call multiple times)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    app_logger.warning(f"Error creating tables (may already exist): {e}")

app = FastAPI(
    title="Authentication Service",
    version="1.0.0",
    description="User authentication, registration, and authorization",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Initialize predefined admin user on startup."""
    db = next(get_db())
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == settings.admin_username).first()
        if not admin:
            # Create predefined admin account
            admin_user = User(
                username=settings.admin_username,
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                role=UserRole.ADMIN,
                approval_status=ApprovalStatus.APPROVED,
                is_active=True,
                first_name="",
                last_name="",
            )
            db.add(admin_user)
            db.commit()
            app_logger.info("Predefined admin user created")
        else:
            app_logger.info("Admin user already exists")
    except Exception as e:
        app_logger.error(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/register", response_model=UserSchema)
async def register(request: UserCreateRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Create new user with PENDING approval status
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        role=UserRole.USER,
        approval_status=ApprovalStatus.PENDING,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT tokens."""
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == request.username_or_email)
        | (User.email == request.username_or_email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Check approval status
    if user.approval_status != ApprovalStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has not been approved yet",
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user,
    )


@app.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information."""
    return current_user


@app.put("/me/profile", response_model=UserSchema)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile information."""
    user = db.query(User).filter(User.id == current_user.id).first()

    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name

    db.commit()
    db.refresh(user)

    return user


# ============================================================================
# Admin Endpoints
# ============================================================================


@app.get("/admin/users", response_model=UserListResponse)
async def list_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get list of all users (admin only)."""
    users = db.query(User).all()
    return UserListResponse(users=users, total=len(users))


@app.get("/admin/users/pending", response_model=UserListResponse)
async def list_pending_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get list of pending approval users (admin only)."""
    users = db.query(User).filter(
        User.approval_status == ApprovalStatus.PENDING
    ).all()
    return UserListResponse(users=users, total=len(users))


@app.get("/admin/users/{user_id}", response_model=UserSchema)
async def get_user_details(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@app.post("/admin/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Approve a pending user registration (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.approval_status = ApprovalStatus.APPROVED
    db.commit()
    db.refresh(user)

    return {"message": "User approved", "user": UserSchema.from_orm(user)}


@app.post("/admin/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Reject a pending user registration (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.approval_status = ApprovalStatus.REJECTED
    db.commit()
    db.refresh(user)

    return {"message": "User rejected", "user": UserSchema.from_orm(user)}


@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Delete or deactivate a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent deletion of the admin user
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account",
        )

    # Deactivate instead of delete
    user.is_active = False
    db.commit()

    return {"message": "User deactivated"}
