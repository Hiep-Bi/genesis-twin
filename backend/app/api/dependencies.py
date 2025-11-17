"""API dependencies - authentication, authorization, etc."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Use raw SQL to avoid enum conversion issues (DB has lowercase role but enum expects uppercase)
    from sqlalchemy import text
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
        WHERE id = :user_id
        LIMIT 1
    """)
    
    result = db.execute(query, {"user_id": user_id}).fetchone()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not result.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create User object from raw SQL result to avoid enum issues
    # Map role string to enum if possible, otherwise use string
    role_str = (result.role or '').upper()
    role_mapping = {
        'ADMIN': UserRole.ADMIN,
        'ENGINEER': UserRole.ENGINEER,
        'OPERATOR': UserRole.OPERATOR,
        'VIEWER': UserRole.VIEWER,
    }
    role_enum = role_mapping.get(role_str, UserRole.VIEWER)
    
    # Create a User instance manually to avoid SQLAlchemy enum conversion
    user = User()
    user.id = result.id
    user.username = result.username
    user.email = result.email
    user.hashed_password = result.hashed_password
    user.full_name = result.full_name
    user.role = role_enum
    user.is_active = result.is_active
    user.created_at = result.created_at
    user.updated_at = result.updated_at
    user.last_login = result.last_login
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


class RoleChecker:
    """Dependency to check user role"""
    
    def __init__(self, required_role: UserRole):
        self.required_role = required_role
    
    def __call__(self, user: User = Depends(get_current_user)) -> User:
        """Check if user has required role"""
        if not user.has_permission(self.required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {self.required_role.value}"
            )
        return user


# Convenience functions for common role checks
require_admin = RoleChecker(UserRole.ADMIN)
require_engineer = RoleChecker(UserRole.ENGINEER)
require_operator = RoleChecker(UserRole.OPERATOR)
require_viewer = RoleChecker(UserRole.VIEWER)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if token is provided, otherwise None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

