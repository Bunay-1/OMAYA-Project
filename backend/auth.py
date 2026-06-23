"""
Authentication & Authorization Module
JWT tokens and RBAC (Role-Based Access Control)
"""
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    roles: List[str] = []
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Mock user database (replace with real DB in production)
# Note: In a real app, these hashes would be generated during user creation.
# The hash below corresponds to 'password123'
DEFAULT_HASH = pwd_context.hash("password123")

fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@omaya-monitoring.com",
        "hashed_password": DEFAULT_HASH,
        "roles": ["admin"],
        "disabled": False,
    },
    "supervisor": {
        "username": "supervisor",
        "email": "supervisor@omaya-monitoring.com",
        "hashed_password": DEFAULT_HASH,
        "roles": ["supervisor"],
        "disabled": False,
    },
    "operator": {
        "username": "operator",
        "email": "operator@omaya-monitoring.com",
        "hashed_password": DEFAULT_HASH,
        "roles": ["operator"],
        "disabled": False,
    }
}

class AuthManager:
    """Manage JWT tokens and user authentication"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with username and password"""
        if username not in fake_users_db:
            return None
        
        user_dict = fake_users_db[username]
        user = UserInDB(**user_dict)
        
        if not AuthManager.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> Token:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return Token(
            access_token=encoded_jwt,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds()) if expires_delta else ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify JWT token and extract data"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            roles: List[str] = payload.get("roles", [])
            
            if username is None:
                return None
            
            return TokenData(username=username, roles=roles)
            
        except JWTError:
            logger.error("Invalid token")
            return None
    
    @staticmethod
    def get_user_roles(username: str) -> List[str]:
        """Get user roles"""
        if username in fake_users_db:
            return fake_users_db[username].get("roles", [])
        return []
    
    @staticmethod
    def has_permission(user_roles: List[str], required_role: str) -> bool:
        """Check if user has required role, considering hierarchy"""
        for role in user_roles:
            if required_role in ROLE_HIERARCHY.get(role, [role]):
                return True
        return False

class RoleChecker:
    """Dependency for checking user roles"""
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    async def __call__(self, token: str) -> TokenData:
        """Check if user has required roles"""
        token_data = AuthManager.verify_token(token)
        
        if token_data is None:
            raise Exception("Invalid token")
        
        # Check if user has any of the required roles
        has_role = any(
            AuthManager.has_permission(token_data.roles, role)
            for role in self.required_roles
        )
        
        if not has_role:
            raise Exception(f"Insufficient permissions. Required: {self.required_roles}")
        
        return token_data

# Role definitions and hierarchies
ROLE_HIERARCHY = {
    "admin": ["admin", "supervisor", "operator"],
    "supervisor": ["supervisor", "operator"],
    "operator": ["operator"]
}

ROLES = {
    "admin": ["read", "write", "delete", "configure", "manage_users"],
    "supervisor": ["read", "write", "delete", "plan_maintenance"],
    "operator": ["read", "read_telemetry"]
}
