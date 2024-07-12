"""Module for creating and disposing connection with db."""

from os import environ as os_environ
from sys import exit as sys_exit

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.project_logger import project_logger


def get_async_engine() -> AsyncEngine:
    """Get asynchronous engine.

    If 'DATABASE_URL' is not set in os environ, call system exit. Then if
    'PYTEST_ASYNC_ENGINE' is set in os environ return asynchronous engine with
    set poolclass=NullPool else without setting poolclass.

    Returns:
        AsyncEngine : asynchronous engine

    """
    db_url = os_environ.get("DATABASE_URL", None)
    project_logger.info(f"{db_url=}")
    if db_url:
        if os_environ.get("PYTEST_ASYNC_ENGINE", None):
            project_logger.info("Creating async engine for pytest")
            return create_async_engine(db_url, poolclass=NullPool)
        project_logger.info("Creating async engine for production")
        return create_async_engine(db_url)
    sys_exit("DATABASE_URL should be set to run the program!")


async def close_db_connection() -> None:
    """Dispose connection with db."""
    project_logger.info("Disposing async engine")
    await async_engine.dispose()


async_engine = get_async_engine()
async_session = async_sessionmaker(bind=async_engine)
Base = declarative_base()
