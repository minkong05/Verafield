"""The bootstrap path. POST /users requires an admin token, so the first
account has to come from outside the request path."""

import pytest

from backend import cli
from backend.db.models.user import User
from shared_types.enums import UserRole


@pytest.fixture
def cli_session(db_session, monkeypatch):
    """Point the CLI at the test transaction. It opens its own SessionLocal
    rather than taking a dependency, which is the whole point of it."""
    monkeypatch.setattr(cli, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(db_session, "close", lambda: None)
    return db_session


def test_create_admin_creates_an_unbound_admin(cli_session) -> None:
    exit_code = cli.main(
        ["create-admin", "--email", "Analyst@TAPAK.example", "--password", "admin-password-12"]
    )

    assert exit_code == 0
    user = cli_session.query(User).filter(User.email == "analyst@tapak.example").one()
    assert user.role == UserRole.ADMIN
    assert user.mill_id is None
    assert user.is_active is True
    assert user.password_hash != "admin-password-12"


def test_create_admin_is_refused_for_an_existing_email(cli_session) -> None:
    args = ["create-admin", "--email", "analyst@tapak.example", "--password", "admin-password-12"]
    assert cli.main(args) == 0

    assert cli.main(args) == 1


def test_create_admin_requires_a_password(monkeypatch) -> None:
    monkeypatch.delenv("TAPAK_ADMIN_PASSWORD", raising=False)

    assert cli.main(["create-admin", "--email", "analyst@tapak.example"]) == 2


def test_create_admin_reads_the_password_from_the_environment(cli_session, monkeypatch) -> None:
    monkeypatch.setenv("TAPAK_ADMIN_PASSWORD", "admin-password-12")

    assert cli.main(["create-admin", "--email", "analyst@tapak.example"]) == 0


def test_create_admin_rejects_a_short_password(monkeypatch) -> None:
    monkeypatch.delenv("TAPAK_ADMIN_PASSWORD", raising=False)

    assert cli.main(["create-admin", "--email", "analyst@tapak.example", "--password", "x"]) == 2
