"""FastAPI dependency for getting the current authenticated user and enforcing RBAC."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt_handler import decode_token
from app.auth.rbac import Permission, Role, has_permission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

DEMO_GUEST_PAYLOAD = {
    "sub": "demo-user-001",
    "role": Role.WORKSPACE_ADMIN.value,
    "email": "guest@researchmind.ai",
    "first_name": "Researcher",
    "last_name": "Guest",
    "workspace_id": "demo-workspace-001",
}


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict:
    """Decode JWT and return the token payload (user info)."""
    if not token or token == "researchmind-demo-guest":
        return DEMO_GUEST_PAYLOAD.copy()

    payload = decode_token(token)
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return payload


def require_permission(permission: Permission):
    """Return a FastAPI dependency that checks the user has a required permission."""
    async def _check(current_user: dict = Depends(get_current_user)) -> dict:
        role_str = current_user.get("role", Role.VIEWER)
        try:
            role = Role(role_str)
        except ValueError:
            role = Role.VIEWER
        if not has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} requires role higher than {role}",
            )
        return current_user
    return _check


def require_role(required_role: Role):
    """Return a FastAPI dependency that checks the user has at least the given role."""
    ROLE_ORDER = [Role.VIEWER, Role.RESEARCHER, Role.WORKSPACE_ADMIN, Role.ORG_ADMIN, Role.SUPER_ADMIN]

    async def _check(current_user: dict = Depends(get_current_user)) -> dict:
        role_str = current_user.get("role", Role.VIEWER)
        try:
            role = Role(role_str)
        except ValueError:
            role = Role.VIEWER
        if ROLE_ORDER.index(role) < ROLE_ORDER.index(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. Required: {required_role}, Got: {role}",
            )
        return current_user
    return _check
