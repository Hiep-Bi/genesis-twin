"""Authentication endpoints"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    security_manager
)
from app.models.user import User, UserRole
from app.api.dependencies import get_current_user
from sqlalchemy import text

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# Request/Response models
class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Registration request"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator("password")
    def validate_password(cls, v):
        is_valid, message = security_manager.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v
    
    @validator("username")
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str
    
    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        if not v or not v.strip():
            raise ValueError('refresh_token is required and cannot be empty')
        return v.strip()


class UserResponse(BaseModel):
    """User response"""
    id: UUID
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    @classmethod
    def from_user(cls, user: User):
        """Create UserResponse from User model, handling role safely"""
        role_value = "viewer"
        try:
            if hasattr(user, 'role'):
                if hasattr(user.role, 'value'):
                    role_value = user.role.value.upper()
                else:
                    role_value = str(user.role).upper()
        except (AttributeError, ValueError):
            role_value = "viewer"
        
        # Normalize role
        role_mapping = {
            'ADMIN': 'admin',
            'ENGINEER': 'engineer',
            'OPERATOR': 'operator',
            'VIEWER': 'viewer',
        }
        role_value = role_mapping.get(role_value, 'viewer')
        
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=role_value,
            is_active=user.is_active,
            created_at=user.created_at
        )
    
    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str
    new_password: str
    
    @validator("new_password")
    def validate_password(cls, v):
        is_valid, message = security_manager.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


# Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **username**: Unique username (3+ alphanumeric chars)
    - **email**: Valid email address
    - **password**: Strong password (8+ chars, uppercase, lowercase, digit)
    - **full_name**: Optional full name
    """
    # Check if username exists
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=UserRole.VIEWER  # Default role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username/email and password
    
    - **username**: Your username or email address
    - **password**: Your password
    
    Returns JWT access token and refresh token
    """
    try:
        # Find user by username or email using raw SQL to avoid enum conversion issues
        # Cast role to text to prevent SQLAlchemy from trying to convert it to enum
        # This handles cases where DB has lowercase role values but enum expects uppercase
        query = text("""
            SELECT 
                id::text as id,
                username,
                email,
                hashed_password,
                full_name,
                role::text as role,
                is_active,
                created_at,
                updated_at,
                last_login
            FROM users
            WHERE username = :username OR email = :username
            LIMIT 1
        """)
        
        result = db.execute(query, {"username": request.username}).fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(request.password, result.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not result.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Get role value safely - role is already a string from CAST
        role_value = (result.role or '').upper() if result.role else 'VIEWER'
        
        # Normalize role value to match enum values
        role_mapping = {
            'ADMIN': 'ADMIN',
            'ENGINEER': 'ENGINEER',
            'OPERATOR': 'OPERATOR',
            'VIEWER': 'VIEWER',
        }
        role_value = role_mapping.get(role_value, 'VIEWER')
        
        user_id = result.id  # Already converted to text
        
        # Update last login using raw SQL
        try:
            # Convert user_id back to UUID for the UPDATE query
            from uuid import UUID
            user_uuid = UUID(user_id)
            update_query = text("""
                UPDATE users
                SET last_login = :last_login
                WHERE id = :user_id
            """)
            db.execute(update_query, {
                "last_login": datetime.utcnow(),
                "user_id": user_uuid
            })
            db.commit()
        except Exception as e:
            # Log error but continue - last_login update is not critical
            db.rollback()
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to update last_login: {e}")
        
        # Create tokens
        access_token = create_access_token({"sub": user_id, "role": role_value})
        refresh_token = create_refresh_token({"sub": user_id})
        
        from app.core.config import settings
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except HTTPException:
        # Re-raise HTTP exceptions (401, 403, etc.)
        raise
    except Exception as e:
        # Log internal errors and return generic error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again."
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and refresh token
    """
    try:
        payload = decode_token(request.refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Get role value safely - handle both enum and string
        try:
            role_value = user.role.value if hasattr(user.role, 'value') else str(user.role)
        except (AttributeError, ValueError):
            # Fallback: try to get role as string or default to 'viewer'
            role_value = getattr(user, 'role', 'viewer')
            if hasattr(role_value, 'upper'):
                role_value = role_value.upper()
            else:
                role_value = 'VIEWER'
        
        # Create new tokens
        access_token = create_access_token({"sub": str(user.id), "role": role_value})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        from app.core.config import settings
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except HTTPException:
        # Re-raise HTTP exceptions (401, 403, etc.)
        raise
    except Exception as e:
        # Log internal errors and return generic error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Refresh token error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during token refresh. Please try again."
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    try:
        # Use UserResponse.from_user to safely handle role conversion
        return UserResponse.from_user(current_user)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting user info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user information"
        )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password for current user
    
    - **old_password**: Current password
    - **new_password**: New password (must meet security requirements)
    """
    # Verify old password
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user
    
    Note: In a stateless JWT system, logout is handled client-side by deleting the token.
    This endpoint is provided for consistency and can be extended with token blacklisting.
    """
    return {"message": "Logged out successfully"}
