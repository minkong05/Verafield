import os
import uuid

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from backend.db.models.mill import Mill
from backend.db.models.user import User
from backend.db.session import get_db, normalize_database_url
from backend.main import app
from backend.services.auth import service as auth_service
from shared_types.auth import UserCreate
from shared_types.enums import MalaysiaState, UserRole

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
def _override_db(db_session):
    """Point the app at the test transaction. Split out of the client fixture
    so several differently-authenticated clients can coexist in one test
    without each clearing the other's override."""

    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(_override_db, admin_token):
    """Authenticated as an admin by default.

    Every mill-scoped route now requires a credential, and an admin reaches
    any mill, so this keeps the Features 01-09 suites testing what they were
    written to test rather than re-testing authorization in 250 places. The
    cost is that those suites never exercise the mill-user path — test_authz.py
    exists to cover exactly that, and is not optional.
    """
    with TestClient(app, headers={"Authorization": f"Bearer {admin_token}"}) as test_client:
        yield test_client


@pytest.fixture
def anon_client(_override_db):
    """No credential at all — for asserting 401s."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def register_mill(db_session):
    """Factory inserting a real mills row and returning its id.

    Hangs off db_session, which the client fixture also binds, so the row is
    visible to TestClient inside the same transaction and rolls back at
    teardown — join_transaction_mode="create_savepoint" makes the commit here
    a savepoint release, exactly as every module-local _make_* helper already
    relies on.

    The licence number is unique per call: uq_mills_mpob_licence_number would
    otherwise make the second call in a two-mill isolation test fail.
    """

    def _register(
        name: str = "Kilang Sawit Tawau",
        state: MalaysiaState = MalaysiaState.SABAH,
    ) -> uuid.UUID:
        mill = Mill(
            name=name,
            mpob_licence_number=f"MPOB-{uuid.uuid4().hex[:12].upper()}",
            postal_address="KM 12, Jalan Apas, 91000 Tawau, Sabah",
            email="ops@kilang-tawau.example",
            district="Tawau",
            state=state,
        )
        db_session.add(mill)
        db_session.commit()
        return mill.id

    return _register


@pytest.fixture
def mill_id(register_mill) -> uuid.UUID:
    """A single registered mill. Most tests want exactly one; the two-mill
    isolation tests use register_mill directly."""
    return register_mill()


@pytest.fixture
def admin_user(db_session) -> User:
    return auth_service.create_user(
        db_session,
        UserCreate(
            email="analyst@tapak.example",
            password="admin-password-12",
            role=UserRole.ADMIN,
        ),
    )


@pytest.fixture
def admin_token(admin_user) -> str:
    token, _ = auth_service.create_access_token(admin_user)
    return token


@pytest.fixture
def make_mill_user(db_session):
    """Factory: a mill_user bound to the given mill, plus its token."""

    def _make(mill_id: uuid.UUID, is_active: bool = True) -> tuple[User, str]:
        user = auth_service.create_user(
            db_session,
            UserCreate(
                email=f"user-{uuid.uuid4().hex[:8]}@kilang.example",
                password="mill-password-12",
                role=UserRole.MILL_USER,
                mill_id=mill_id,
            ),
        )
        if not is_active:
            user = auth_service.set_user_active(db_session, user.id, False)
        token, _ = auth_service.create_access_token(user)
        return user, token

    return _make


@pytest.fixture
def mill_client(_override_db, make_mill_user):
    """Factory: a TestClient authenticated as a mill_user of the given mill."""

    def _make(mill_id: uuid.UUID) -> TestClient:
        _, token = make_mill_user(mill_id)
        return TestClient(app, headers={"Authorization": f"Bearer {token}"})

    return _make
