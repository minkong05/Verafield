import uuid
from datetime import UTC, datetime, timedelta
from functools import lru_cache

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import Session

from backend.db.models.user import User
from packages.shared_types.auth import UserCreate
from packages.shared_types.enums import UserRole

__all__ = [
    "AuthSettings",
    "InvalidCredentialsError",
    "InvalidRoleAssignmentError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "authenticate_user",
    "change_password",
    "create_access_token",
    "create_user",
    "decode_access_token",
    "get_auth_settings",
    "get_user",
    "hash_password",
    "list_users",
    "normalise_email",
    "set_user_active",
    "verify_password",
]


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # RFC 7518 section 3.2: an HMAC key for HS256 must be at least as long
    # as the hash output. PyJWT only warns; rejecting a short key here turns
    # that into a loud configuration failure instead of a per-request warning
    # nobody reads.
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_ttl_hours: int = 12


@lru_cache
def get_auth_settings() -> AuthSettings:
    """Resolved lazily, on first use, rather than at import time.

    DatabaseSettings is read at import in backend/db/session.py because the
    engine is built there. Copying that here would make backend.main
    unimportable without JWT_SECRET_KEY set, which would break
    backend/tests/test_health.py's module-level TestClient and the CI
    docker-build job's anonymous /health probe. jwt_secret_key still has no
    default: a shipped fallback secret is worse than a loud failure on the
    first authentication attempt."""
    return AuthSettings()


class InvalidCredentialsError(Exception):
    """The email/password pair does not identify an active user."""


class UserNotFoundError(Exception):
    """No user exists with the given id."""


class UserAlreadyExistsError(Exception):
    """A user is already registered with that email address."""


class InvalidRoleAssignmentError(Exception):
    """An admin may not be bound to a mill, and a mill user must be."""


_hasher = PasswordHasher()

# Argon2 verification is deliberately run even when no user matched, against
# this hash of a value no one can supply, so a failed login takes the same
# time whether or not the account exists. Without it, response latency is an
# account-enumeration oracle — the same class of leak
# docs/roadmap/11-mill-authentication.md asks this feature to close.
_DUMMY_HASH = _hasher.hash("argon2-timing-equaliser-not-a-password")


def normalise_email(email: str) -> str:
    """Lowercased and stripped on every write and every lookup, which is what
    makes uq_users_email a case-insensitive constraint without citext."""
    return email.strip().lower()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """argon2's verify() raises rather than returning False, and raises a
    different exception for a malformed stored hash than for a mismatch;
    both mean "not authenticated" here."""
    try:
        return _hasher.verify(password_hash, password)
    except Argon2Error:
        return False


def create_access_token(user: User) -> tuple[str, datetime]:
    """Returns the token and its expiry.

    The only claims are sub/iat/exp. Role and mill_id are deliberately absent:
    they are re-read from the database on each request, so deactivating a user
    or moving them between mills takes effect immediately instead of waiting
    out a token's lifetime, and there is exactly one source of truth for
    authorization rather than two that can disagree."""
    settings = get_auth_settings()
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(hours=settings.access_token_ttl_hours)
    token = jwt.encode(
        {"sub": str(user.id), "iat": issued_at, "exp": expires_at},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_at


def decode_access_token(token: str) -> uuid.UUID:
    """The user id from a valid, unexpired token. Raises
    InvalidCredentialsError for anything else — a bad signature, an expired
    token and a malformed one are indistinguishable to the caller by design."""
    settings = get_auth_settings()
    try:
        claims = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return uuid.UUID(claims["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise InvalidCredentialsError("invalid or expired token") from exc


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == normalise_email(email)).one_or_none()
    if user is None:
        verify_password(_DUMMY_HASH, password)
        raise InvalidCredentialsError("incorrect email or password")
    if not verify_password(user.password_hash, password):
        raise InvalidCredentialsError("incorrect email or password")
    if not user.is_active:
        # Same message and same status as a wrong password: whether an account
        # exists but is deactivated is not something an unauthenticated caller
        # should be able to determine.
        raise InvalidCredentialsError("incorrect email or password")
    return user


def get_user(db: Session, user_id: uuid.UUID) -> User:
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        raise UserNotFoundError(f"no user with id {user_id}")
    return user


def list_users(db: Session, mill_id: uuid.UUID | None = None) -> list[User]:
    query = db.query(User)
    if mill_id is not None:
        query = query.filter(User.mill_id == mill_id)
    return query.order_by(User.email).all()


def create_user(db: Session, payload: UserCreate) -> User:
    """Mirrors ck_users_role_mill_id in application code so the caller gets a
    422 naming the problem rather than a 500 from the constraint. The
    constraint remains the actual guarantee."""
    if payload.role == UserRole.ADMIN and payload.mill_id is not None:
        raise InvalidRoleAssignmentError("an admin user must not be bound to a mill")
    if payload.role == UserRole.MILL_USER and payload.mill_id is None:
        raise InvalidRoleAssignmentError("a mill user must be bound to a mill")

    email = normalise_email(payload.email)
    if db.query(User).filter(User.email == email).one_or_none() is not None:
        raise UserAlreadyExistsError(f"a user is already registered with email {email}")

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        mill_id=payload.mill_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_user_active(db: Session, user_id: uuid.UUID, is_active: bool) -> User:
    """Revocation. Takes effect on the user's next request, not on their next
    login, because get_current_user re-reads this column every time."""
    user = get_user(db, user_id)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> User:
    if not verify_password(user.password_hash, current_password):
        raise InvalidCredentialsError("current password is incorrect")
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user
