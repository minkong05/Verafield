from collections.abc import Generator
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str


@lru_cache
def get_settings() -> DatabaseSettings:
    return DatabaseSettings()


def normalize_database_url(url: str) -> str:
    """A bare postgresql:// URL resolves to the psycopg2 dialect, which isn't
    installed (only psycopg[binary]>=3.2 is a project dependency). Force the
    psycopg3 dialect explicitly so engine creation doesn't fail."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(
    normalize_database_url(get_settings().database_url), pool_pre_ping=True, future=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
