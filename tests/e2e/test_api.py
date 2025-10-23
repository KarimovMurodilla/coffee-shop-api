"""
End-to-end tests for API endpoints.
These tests simulate real HTTP requests to the API.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.database.connection import get_db_session
from app.infrastructure.database.models import Base
from app.main import app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine):
    """Override database session for tests."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db

    yield

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(test_db_session):
    """Create test HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_signup_creates_user(self, client):
        """Test user signup."""
        response = await client.post(
            "/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["is_verified"] is False
        assert "id" in data

    @pytest.mark.asyncio
    async def test_signup_rejects_duplicate_email(self, client):
        """Test signup rejects duplicate email."""
        # Create first user
        await client.post(
            "/auth/signup",
            json={"email": "duplicate@example.com", "password": "Password123!"},
        )

        # Try to create second user with same email
        response = await client.post(
            "/auth/signup",
            json={"email": "duplicate@example.com", "password": "DifferentPass123!"},
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_signup_validates_email_format(self, client):
        """Test signup validates email format."""
        response = await client.post(
            "/auth/signup", json={"email": "invalid-email", "password": "Password123!"}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_signup_requires_password_minimum_length(self, client):
        """Test signup requires minimum password length."""
        response = await client.post(
            "/auth/signup", json={"email": "user@example.com", "password": "short"}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_returns_tokens(self, client):
        """Test login returns access and refresh tokens."""
        # First, create a verified user
        await client.post(
            "/auth/signup",
            json={"email": "loginuser@example.com", "password": "LoginPass123!"},
        )

        # For testing, we'll need to manually verify the user
        # In real tests, you would extract the verification code from logs/emails
        # For now, we'll test login with the unverified user (should still work)

        response = await client.post(
            "/auth/login",
            json={"email": "loginuser@example.com", "password": "LoginPass123!"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_rejects_wrong_password(self, client):
        """Test login rejects wrong password."""
        # Create user
        await client.post(
            "/auth/signup",
            json={"email": "testuser@example.com", "password": "CorrectPass123!"},
        )

        # Try to login with wrong password
        response = await client.post(
            "/auth/login",
            json={"email": "testuser@example.com", "password": "WrongPass123!"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_rejects_nonexistent_user(self, client):
        """Test login rejects non-existent user."""
        response = await client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "Password123!"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_returns_new_access_token(self, client):
        """Test refresh token endpoint."""
        # Create and login user
        await client.post(
            "/auth/signup",
            json={"email": "refresh@example.com", "password": "Pass123!"},
        )

        login_response = await client.post(
            "/auth/login", json={"email": "refresh@example.com", "password": "Pass123!"}
        )

        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token to get new access token
        response = await client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["refresh_token"] == refresh_token


class TestUserEndpoints:
    """Test user management endpoints."""

    async def _create_and_login_user(self, client, email, password, is_admin=False):
        """Helper method to create and login a user."""
        await client.post("/auth/signup", json={"email": email, "password": password})

        login_response = await client.post(
            "/auth/login", json={"email": email, "password": password}
        )

        return login_response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_get_current_user(self, client):
        """Test GET /users/me endpoint."""
        token = await self._create_and_login_user(
            client, "currentuser@example.com", "Pass123!"
        )

        response = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "currentuser@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_requires_auth(self, client):
        """Test /users/me requires authentication."""
        response = await client.get("/users/me")

        assert response.status_code == 403  # No auth header

    @pytest.mark.asyncio
    async def test_get_current_user_rejects_invalid_token(self, client):
        """Test /users/me rejects invalid token."""
        response = await client.get(
            "/users/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_own_user(self, client):
        """Test user can update their own information."""
        # Create and login
        await client.post(
            "/auth/signup",
            json={
                "email": "updateme@example.com",
                "password": "Pass123!",
                "first_name": "Old",
                "last_name": "Name",
            },
        )

        login_response = await client.post(
            "/auth/login",
            json={"email": "updateme@example.com", "password": "Pass123!"},
        )

        token = login_response.json()["access_token"]

        # Get current user to find ID
        me_response = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        user_id = me_response.json()["id"]

        # Update user
        response = await client.patch(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "New", "last_name": "Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "New"
        assert data["last_name"] == "Name"

    @pytest.mark.asyncio
    async def test_partial_update_user(self, client):
        """Test partial update (only some fields)."""
        token = await self._create_and_login_user(
            client, "partial@example.com", "Pass123!"
        )

        me_response = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        user_id = me_response.json()["id"]

        # Update only first name
        response = await client.patch(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "OnlyFirst"},
        )

        assert response.status_code == 200
        assert response.json()["first_name"] == "OnlyFirst"


class TestAuthenticationFlow:
    """Test complete authentication flows."""

    @pytest.mark.asyncio
    async def test_complete_signup_login_flow(self, client):
        """
        Test complete authentication flow
        from signup to accessing protected resource.
        """
        # 1. Signup
        signup_response = await client.post(
            "/auth/signup",
            json={
                "email": "fullflow@example.com",
                "password": "SecurePass123!",
                "first_name": "Full",
                "last_name": "Flow",
            },
        )
        assert signup_response.status_code == 201
        user_data = signup_response.json()
        assert user_data["email"] == "fullflow@example.com"

        # 2. Login
        login_response = await client.post(
            "/auth/login",
            json={"email": "fullflow@example.com", "password": "SecurePass123!"},
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]

        # 3. Access protected resource
        me_response = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == "fullflow@example.com"
        assert me_data["first_name"] == "Full"
