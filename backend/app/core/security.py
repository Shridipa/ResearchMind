import jwt
from datetime import datetime, timedelta
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

SECRET_KEY = "enterprise-super-secret-key-do-not-use-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class SecurityManager:
    """Enterprise Security Manager handling JWT and RBAC."""

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def check_permissions(user_roles: List[str], required_permission: str) -> bool:
        # Simulated RBAC map
        role_permissions = {
            "admin": ["read", "write", "delete", "api:call", "db:read", "calc:execute", "search:read", "doc:read"],
            "analyst": ["read", "search:read", "calc:execute"],
            "guest": ["read"]
        }
        
        user_perms = set()
        for role in user_roles:
            user_perms.update(role_permissions.get(role, []))
            
        return required_permission in user_perms
