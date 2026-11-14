import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


def resolve_db_connection() -> tuple[str, dict]:
    # Priority 1: explicitly passed environment variable
    raw_url = os.getenv("DATABASE_URL")
    
    # Priority 2: settings value if it's not the default unreachable localhost
    if not raw_url and settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL:
        raw_url = settings.DATABASE_URL

    connect_args = {}

    if raw_url and ("postgres" in raw_url or "neon.tech" in raw_url):
        if raw_url.startswith("postgres://"):
            raw_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif raw_url.startswith("postgresql://"):
            raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        parsed = urlparse(raw_url)
        query_params = parse_qs(parsed.query)
        if "sslmode" in query_params:
            ssl_val = query_params.pop("sslmode")[0]
            if ssl_val in ("require", "verify-ca", "verify-full"):
                connect_args["ssl"] = True
        elif parsed.hostname and "neon.tech" in parsed.hostname:
            connect_args["ssl"] = True

        new_query = urlencode(query_params, doseq=True)
        raw_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        return raw_url, connect_args

    # Default to resilient local storage when no external Neon DB URL is configured
    return "sqlite+aiosqlite:///./cognify.db", {"check_same_thread": False}


db_url, connect_args = resolve_db_connection()

engine = create_async_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
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
    async with engine.begin() as conn:
        import app.models  # noqa
        await conn.run_sync(Base.metadata.create_all)
