"""
Shared test fixtures for the auth system test suite.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db.session import get_session
from src.core.rate_limit import limiter


@pytest_asyncio.fixture(name="session")
async def session_fixture():
    """Create an async in-memory SQLite test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(name="client")
async def client_fixture(session):
    """Create a test client with mocked database session."""
    # Disable rate limiting during tests
    limiter.enabled = False

    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    limiter.enabled = True


@pytest_asyncio.fixture(name="registered_user")
async def registered_user_fixture(client):
    """Register a test user and return (email, password, tokens)."""
    email = "testuser@example.com"
    password = "SecurePassword123"

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    data = response.json()
    return {
        "email": email,
        "password": password,
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }


@pytest_asyncio.fixture(name="admin_user")
async def admin_user_fixture(client, session):
    """Register a user and promote to admin via database."""
    email = "admin@example.com"
    password = "AdminPassword123"

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    data = response.json()

    # Promote to admin directly in the database
    from src.models.models import User

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalars().first()
    user.role = "admin"
    session.add(user)
    await session.commit()

    return {
        "email": email,
        "password": password,
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "user_id": str(user.id),
    }
