"""
Comprehensive test suite for the Auth System PRO API.

Covers: register, login, refresh, logout, /me, password change,
edge cases (duplicate email, invalid credentials, expired tokens, etc.)
"""
import pytest
from tests.helpers import auth_header


# ═══════════════════════════════════════════════════════════════════════
# Registration Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_register_success(client):
    """Test successful user registration returns both tokens."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "SecurePassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Test registration with duplicate email returns 409."""
    payload = {"email": "dupe@example.com", "password": "SecurePassword123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Test registration with invalid email returns 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "SecurePassword123"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client):
    """Test registration with password too short returns 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_password_no_uppercase(client):
    """Test registration with password missing uppercase returns 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "noup@example.com", "password": "securepass123"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_password_no_digit(client):
    """Test registration with password missing digit returns 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "nodigit@example.com", "password": "SecurePassword"},
    )
    assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════
# Login Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_login_success(client, registered_user):
    """Test successful login returns tokens."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, registered_user):
    """Test login with wrong password returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with non-existent user returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════
# Token Refresh Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_refresh_success(client, registered_user):
    """Test successful token refresh returns new tokens."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": registered_user["refresh_token"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # New refresh token should be different (rotation)
    assert data["refresh_token"] != registered_user["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_reuse_revoked_token(client, registered_user):
    """Test using a revoked refresh token fails (rotation security)."""
    old_refresh = registered_user["refresh_token"]

    # First refresh — consumes the token
    await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )

    # Second refresh with same token — should fail (reuse detection)
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    """Test refresh with garbage token returns 401."""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )
    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════
# Logout Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_logout_success(client, registered_user):
    """Test successful logout revokes the refresh token."""
    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": registered_user["refresh_token"]},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"

    # Verify token is revoked — refresh should fail
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": registered_user["refresh_token"]},
    )
    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════
# User Profile Tests (/me)
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_get_me_authenticated(client, registered_user):
    """Test GET /me with valid token returns user profile."""
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_header(registered_user["access_token"]),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == registered_user["email"]
    assert data["role"] == "user"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_no_token(client):
    """Test GET /me without token returns 403."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me_invalid_token(client):
    """Test GET /me with invalid token returns 401."""
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_header("invalid.token.here"),
    )
    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════
# Password Change Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_change_password_success(client, registered_user):
    """Test successful password change."""
    response = await client.put(
        "/api/v1/users/me/password",
        headers=auth_header(registered_user["access_token"]),
        json={
            "current_password": registered_user["password"],
            "new_password": "newSecurePass456",
        },
    )
    assert response.status_code == 200
    assert "changed" in response.json()["message"].lower()

    # Verify new password works for login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": "newSecurePass456",
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current(client, registered_user):
    """Test password change with wrong current password fails."""
    response = await client.put(
        "/api/v1/users/me/password",
        headers=auth_header(registered_user["access_token"]),
        json={
            "current_password": "wrongpassword",
            "new_password": "newSecurePass456",
        },
    )
    assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════
# System Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


# ═══════════════════════════════════════════════════════════════════════
# Admin Route Tests
# ═══════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_list_users_as_admin(client, admin_user):
    """Test admin can list all users."""
    response = await client.get(
        "/api/v1/users/",
        headers=auth_header(admin_user["access_token"]),
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Verify response structure
    assert "id" in data[0]
    assert "email" in data[0]
    assert "role" in data[0]


@pytest.mark.asyncio
async def test_list_users_as_regular_user(client, registered_user):
    """Test regular user cannot list users (403)."""
    response = await client.get(
        "/api/v1/users/",
        headers=auth_header(registered_user["access_token"]),
    )
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_users_no_auth(client):
    """Test listing users without auth returns 403."""
    response = await client.get("/api/v1/users/")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_toggle_user_status_as_admin(client, admin_user):
    """Test admin can deactivate a user."""
    # Create a regular user to toggle
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "toggleme@example.com", "password": "SecurePass123"},
    )
    assert reg.status_code == 201

    # Get user list to find the target user's ID
    list_resp = await client.get(
        "/api/v1/users/",
        headers=auth_header(admin_user["access_token"]),
    )
    users = list_resp.json()
    target = next(u for u in users if u["email"] == "toggleme@example.com")

    # Deactivate the user
    response = await client.put(
        f"/api/v1/users/{target['id']}/status",
        headers=auth_header(admin_user["access_token"]),
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Reactivate the user
    response = await client.put(
        f"/api/v1/users/{target['id']}/status",
        headers=auth_header(admin_user["access_token"]),
        json={"is_active": True},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_toggle_user_status_as_regular_user(client, registered_user):
    """Test regular user cannot toggle user status (403)."""
    fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.put(
        f"/api/v1/users/{fake_uuid}/status",
        headers=auth_header(registered_user["access_token"]),
        json={"is_active": False},
    )
    assert response.status_code == 403

