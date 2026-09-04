import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.base import Base
from packages.shared_types.enums import UserRole

_user_role_type = SAEnum(UserRole, name="user_role", values_callable=lambda e: [m.value for m in e])


class User(Base):
    """A person who can authenticate, under one of two principal kinds: an
    admin (TAPAK staff — the compliance analyst the roadmap docs name) or a
    mill user acting for exactly one mill. Roles *within* a mill are out of
    scope (docs/roadmap/11-mill-authentication.md).

    ck_users_role_mill_id is the load-bearing constraint here, and it is the
    reason mill_id is nullable at all: an admin can never be pinned to a
    tenant, and a mill user can never be tenant-less, enforced in the schema
    rather than left to application code — the same commitment
    backend/db/README.md's hard rule makes for tenant isolation.

    Not a tenant table, despite carrying mill_id: users sit alongside mills at
    the root, so there is no UNIQUE(id, mill_id) and children never compose a
    key with it. The FK is plain and RESTRICT, like every other reference to
    mills.

    email is stored lowercased by auth.service on both write and lookup, so a
    plain UNIQUE constraint gives case-insensitive uniqueness without the
    citext extension. password_hash holds an Argon2id encoded hash and is
    exposed by no schema anywhere. is_active is the revocation mechanism —
    it is re-read from the database on every request rather than trusted from
    a token claim, so revoking access does not wait for a token to expire."""

    __tablename__ = "users"
    __table_args__ = (
        ForeignKeyConstraint(["mill_id"], ["mills.id"], name="fk_users_mill"),
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint(
            "(role = 'admin' AND mill_id IS NULL) OR (role = 'mill_user' AND mill_id IS NOT NULL)",
            name="ck_users_role_mill_id",
        ),
        Index("ix_users_mill_id", "mill_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(_user_role_type, nullable=False)
    mill_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
