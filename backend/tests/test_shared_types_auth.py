import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from shared_types.auth import TokenResponse, User, UserCreate
from shared_types.enums import UserRole


def test_user_create_accepts_a_mill_user() -> None:
    mill_id = uuid.uuid4()

    user = UserCreate(
        email="procurement@kilang-tawau.example",
        password="mill-password-12",
        role=UserRole.MILL_USER,
        mill_id=mill_id,
    )

    assert user.role == UserRole.MILL_USER
    assert user.mill_id == mill_id


def test_user_create_defaults_mill_id_to_none_for_an_admin() -> None:
    user = UserCreate(
        email="analyst@tapak.example", password="admin-password-12", role=UserRole.ADMIN
    )

    assert user.mill_id is None


def test_user_create_rejects_a_short_password() -> None:
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.example", password="short", role=UserRole.ADMIN)


def test_user_create_rejects_an_unknown_role() -> None:
    with pytest.raises(ValidationError):
        UserCreate(email="a@b.example", password="admin-password-12", role="superuser")


def test_user_read_model_declares_no_password_field() -> None:
    """The read model lists its fields explicitly precisely so that
    from_attributes can never surface password_hash off the ORM row."""
    assert "password" not in User.model_fields
    assert "password_hash" not in User.model_fields


def test_user_read_model_round_trips() -> None:
    now = datetime.now(UTC)

    user = User(
        id=uuid.uuid4(),
        email="analyst@tapak.example",
        role=UserRole.ADMIN,
        mill_id=None,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    assert user.is_active is True
    assert user.mill_id is None


def test_token_response_defaults_to_the_bearer_scheme() -> None:
    token = TokenResponse(access_token="abc", expires_at=datetime.now(UTC))

    assert token.token_type == "bearer"
