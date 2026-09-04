import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from shared_types.enums import UserRole


class UserBase(BaseModel):
    email: str
    role: UserRole
    # None for an admin, required for a mill user — enforced in the service
    # and, structurally, by ck_users_role_mill_id.
    mill_id: uuid.UUID | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=12)


class User(UserBase):
    """Read model. Deliberately declares every field it exposes rather than
    mirroring the ORM row: password_hash has no field here, so
    from_attributes can never surface it."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Revocation only. Role and mill assignment are fixed at creation for
    MVP — changing either is a re-issue, not an edit."""

    is_active: bool


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12)
