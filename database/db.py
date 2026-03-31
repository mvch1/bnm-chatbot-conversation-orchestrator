"""
Database engine and session factory.

Usage:
    from database.db import get_db

    async with get_db() as db:
        db.add(some_model)
        await db.commit()
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://chatbot_user:motdepasse@localhost:5432/banking_chatbot",
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db():
    """Provide a transactional database session."""
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
    """Create all tables (use only in dev / migrations)."""
    from database.models import Base  # noqa: F401 – triggers model registration
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
