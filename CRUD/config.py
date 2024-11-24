import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

project_root = Path(__file__).parent.parent

database_url = os.getenv('DATABASE_CONNECTION_STRING')
if not database_url:
    raise ValueError(
        "DATABASE_CONNECTION_STRING environment variable is not set. "
        "Please set it to your Neon database connection string"
    )

if 'postgresql+asyncpg://' not in database_url:
    database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')

engine = create_async_engine(
    database_url,
    echo=True,  # Set to False in production
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "server_settings": {
            "application_name": "PYS_App",
            "statement_timeout": "60000",
            "idle_in_transaction_session_timeout": "60000"
        }
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
            yield session
        except Exception as e:
            await session.rollback()
            raise ConnectionError(f"Database connection failed: {str(e)}")
        finally:
            await session.close()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        raise ConnectionError(f"Failed to initialize database: {str(e)}")

async def close_db():
    try:
        await engine.dispose()
    except Exception as e:
        raise ConnectionError(f"Failed to properly close database connections: {str(e)}")