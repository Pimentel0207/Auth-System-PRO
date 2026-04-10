import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db.session import get_session
from src.models.models import User
from src.schemas.schemas import RegisterRequest, LoginRequest


@pytest_asyncio.fixture(name="session")
async def session_fixture():
    """Create an async test database session."""
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
    """Create a test client with mock session."""

    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_success(client, session):
    """Test successful user registration."""
    payload = {
        "email": "testuser@example.com",
        "password": "securepassword123"
    }

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800  # 30 minutes


@pytest.mark.asyncio
async def test_register_duplicate_email(client, session):
    """Test registration with duplicate email."""
    # First registration
    payload = {
        "email": "testuser@example.com",
        "password": "securepassword123"
    }

    await client.post("/api/v1/auth/register", json=payload)

    # Second registration with same email
    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Test registration with invalid email."""
    payload = {
        "email": "invalid-email",
        "password": "securepassword123"
    }

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_short_password(client):
    """Test registration with password too short."""
    payload = {
        "email": "testuser@example.com",
        "password": "short"
    }

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(client, session):
    """Test successful login."""
    # First register
    register_payload = {
        "email": "testuser@example.com",
        "password": "securepassword123"
    }

    await client.post("/api/v1/auth/register", json=register_payload)

    # Then login
    login_payload = {
        "email": "testuser@example.com",
        "password": "securepassword123"
    }

    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, session):
    """Test login with invalid credentials."""
    # First register
    register_payload = {
        "email": "testuser@example.com",
        "password": "securepassword123"
    }

    await client.post("/api/v1/auth/register", json=register_payload)

    # Try login with wrong password
    login_payload = {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    }

    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    payload = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }

    response = await client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint."""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["version"] == "0.1.0"
