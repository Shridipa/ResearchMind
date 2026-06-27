"""
RBAC - Role-Based Access Control
Roles: SUPER_ADMIN, ORG_ADMIN, WORKSPACE_ADMIN, RESEARCHER, VIEWER
"""
from enum import Enum


class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    WORKSPACE_ADMIN = "WORKSPACE_ADMIN"
    RESEARCHER = "RESEARCHER"
    VIEWER = "VIEWER"


class Permission(str, Enum):
    CREATE_WORKSPACE = "create_workspace"
    DELETE_WORKSPACE = "delete_workspace"
    UPLOAD_DOCUMENTS = "upload_documents"
    DELETE_DOCUMENTS = "delete_documents"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    RUN_RESEARCH = "run_research"
    VIEW_ANALYTICS = "view_analytics"
    VIEW_ADMIN_PANEL = "view_admin_panel"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),
    Role.ORG_ADMIN: {
        Permission.CREATE_WORKSPACE,
        Permission.DELETE_WORKSPACE,
        Permission.UPLOAD_DOCUMENTS,
        Permission.DELETE_DOCUMENTS,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.RUN_RESEARCH,
        Permission.VIEW_ANALYTICS,
    },
    Role.WORKSPACE_ADMIN: {
        Permission.UPLOAD_DOCUMENTS,
        Permission.DELETE_DOCUMENTS,
        Permission.MANAGE_USERS,
        Permission.RUN_RESEARCH,
        Permission.VIEW_ANALYTICS,
    },
    Role.RESEARCHER: {
        Permission.UPLOAD_DOCUMENTS,
        Permission.RUN_RESEARCH,
        Permission.VIEW_ANALYTICS,
    },
    Role.VIEWER: set(),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
