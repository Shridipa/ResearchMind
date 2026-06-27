from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey
from .base import BaseModel
from typing import List

class Organization(BaseModel):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=True)

    users: Mapped[List["User"]] = relationship(back_populates="organization")
    workspaces: Mapped[List["Workspace"]] = relationship(back_populates="organization")

class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    organization: Mapped["Organization"] = relationship(back_populates="users")

    workspace_memberships: Mapped[List["WorkspaceMember"]] = relationship(back_populates="user")
