import os

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from backend.db.session import get_db, normalize_database_url
from backend.main import app

DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg://tapak:tapak@localhost:5432/tapak_test"
TEST_DATABASE_URL = normalize_database_url(
    os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
)


def _ensure_test_database_exists() -> None:
    admin_url = TEST_DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    db_name = TEST_DATABASE_URL.rsplit("/", 1)[1]
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": db_name}
        ).first()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    admin_engine.dispose()


@pytest.fixture(scope="session")
def _migrated_test_db():
    _ensure_test_database_exists()
    engine = create_engine(TEST_DATABASE_URL)
    cfg = Config("backend/alembic.ini")
    with engine.connect() as connection:
        # Passing a live connection (Alembic's documented "Programmatic Use
        # in a Test Suite" recipe) rather than sqlalchemy.url so this always
        # targets TEST_DATABASE_URL, regardless of what DATABASE_URL/.env
        # resolves to for the app itself.
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")
        connection.commit()
    yield
    with engine.connect() as connection:
        cfg.attributes["connection"] = connection
        command.downgrade(cfg, "base")
        connection.commit()
    engine.dispose()


@pytest.fixture
def db_session(_migrated_test_db):
    engine = create_engine(TEST_DATABASE_URL)
    connection = engine.connect()
    transaction = connection.begin()
    # create_savepoint: a test that triggers an IntegrityError (and thus a
    # session-level rollback) still leaves the outer transaction usable, so
    # the fixture's own rollback below always has something to roll back.
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()
    engine.dispose()


@pytest.fixture
def client(db_session):
    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
