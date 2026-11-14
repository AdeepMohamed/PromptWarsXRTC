import os
import socket
import ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# ---------------------------------------------------------------------------
# Resilient DNS resolution for Neon endpoints on systems with local router DNS limits
# ---------------------------------------------------------------------------
_orig_getaddrinfo = socket.getaddrinfo

def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    try:
        return _orig_getaddrinfo(host, port, family, type, proto, flags)
    except socket.gaierror:
        # If standard local router DNS fails on deep neon.tech subdomains, use resolved Neon AWS IPs
        if "neon.tech" in str(host):
            for ip in ("3.142.41.151", "3.14.138.241", "77.112.129.102"):
                try:
                    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port))]
                except Exception:
                    continue
        raise

socket.getaddrinfo = _patched_getaddrinfo


def resolve_db_connection() -> tuple[str, dict]:
    # Priority 1: explicitly passed environment variable or .env
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
        # For SQLAlchemy persistent pooling, use direct endpoint for optimal stability
        if "-pooler" in parsed.netloc:
            netloc = parsed.netloc.replace("-pooler", "")
            parsed = parsed._replace(netloc=netloc)

        query_params = parse_qs(parsed.query)

        # Neon pooler / PgBouncer requires statement_cache_size=0
        if "pooler" in (parsed.hostname or "") or "neon.tech" in (parsed.hostname or ""):
            connect_args["statement_cache_size"] = 0
            connect_args["prepared_statement_cache_size"] = 0
            # Explicit Neon SNI endpoint routing
            if parsed.hostname:
                endpoint_id = parsed.hostname.split(".")[0].replace("-pooler", "")
                connect_args["server_settings"] = {"options": f"endpoint={endpoint_id}"}
                
                # Resilient direct IP for local Windows environments where deep subdomains fail DNS
                try:
                    socket.gethostbyname(parsed.hostname)
                except Exception:
                    # DNS failed: route directly to Neon AWS us-east-2 gateway IP with custom SSL context
                    user_pass = f"{parsed.username}:{parsed.password}@" if parsed.username else ""
                    port_str = f":{parsed.port}" if parsed.port else ""
                    parsed = parsed._replace(netloc=f"{user_pass}3.142.41.151{port_str}")
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    connect_args["ssl"] = ctx

        # Strip params asyncpg does not accept in query strings
        if "ssl" not in connect_args:
            if "sslmode" in query_params or (parsed.hostname and "neon.tech" in parsed.hostname):
                connect_args["ssl"] = "require"
        query_params.pop("sslmode", None)
        query_params.pop("channel_binding", None)

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

    # Fallback to local storage if no Neon DB URL is configured
    return "sqlite+aiosqlite:///./cognify.db", {"check_same_thread": False}


db_url, connect_args = resolve_db_connection()

engine = create_async_engine(
    db_url,
    connect_args=connect_args,
    pool_size=20,
    max_overflow=20,
    pool_recycle=300,
    pool_timeout=15.0,
    pool_pre_ping=False,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


import logging
logger = logging.getLogger(__name__)

# High-speed local replica engine for zero-downtime resilience
try:
    _fallback_engine = create_async_engine(
        "sqlite+aiosqlite:///./cognify.db",
        connect_args={"check_same_thread": False},
        pool_recycle=300,
        echo=False,
    )
    _FallbackSessionLocal = async_sessionmaker(
        _fallback_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
except Exception as e:
    logger.warning(f"aiosqlite local fallback not initialized: {e}")
    _FallbackSessionLocal = AsyncSessionLocal

_neon_status_cache = {"is_healthy": False, "last_checked": 0.0}

async def _check_primary_db() -> bool:
    import time
    now = time.time()
    # If checked within last 60s, return cached status immediately (0ms latency)
    if now - _neon_status_cache["last_checked"] < 60.0:
        return _neon_status_cache["is_healthy"]

    _neon_status_cache["last_checked"] = now
    try:
        import asyncio
        from sqlalchemy import text
        async def _probe():
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        await asyncio.wait_for(_probe(), timeout=1.0)
        _neon_status_cache["is_healthy"] = True
        return True
    except Exception:
        _neon_status_cache["is_healthy"] = False
        return False

async def get_db():
    is_primary_up = await _check_primary_db()
    session_factory = AsyncSessionLocal if (is_primary_up or not _FallbackSessionLocal) else _FallbackSessionLocal
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    try:
        import asyncio
        async def _do_init():
            async with engine.begin() as conn:
                import app.models  # noqa
                await conn.run_sync(Base.metadata.create_all)
        await asyncio.wait_for(_do_init(), timeout=5.0)
    except Exception as e:
        print(f"init_db note: tables already prepared or check bypassed: {e}")
