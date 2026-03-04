#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Database configuration and session management."""
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from ..settings import environment_config

logger = logging.getLogger(__name__)

# Prepare engine arguments based on database type
db_url = environment_config.SQLALCHEMY_DATABASE_URL

if db_url.startswith("sqlite"):
    engine_args = {
        "echo": False,
        "future": True,
        "connect_args": {"check_same_thread": False}
    }
    logger.info(f"Using SQLite database")
elif db_url.startswith("postgresql"):
    engine_args = {
        "echo": False,
        "future": True,
        "pool_size": 5,
        "max_overflow": 10,
    }
    logger.info(f"Using PostgreSQL database")
else:
    engine_args = {
        "echo": False,
        "future": True,
    }
    logger.info(f"Using database: {db_url[:20]}...")

# Create async engine
engine = create_async_engine(
    db_url,
    **engine_args
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully")


def main():
    """Main function for testing."""
    print(f"Database URL: {environment_config.SQLALCHEMY_DATABASE_URL}")


if __name__ == "__main__":
    main()
