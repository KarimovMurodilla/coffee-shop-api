"""
Unit tests for application use cases.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.dto import (
    LoginRequest,
    SignupRequest,
    UpdateUserRequest,
    VerifyRequest,
)
from app.application.exceptions import (
    ForbiddenError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    VerificationError,
)
from app.application.use_cases.auth import (
    LoginUseCase,
    SignupUseCase,
    VerifyEmailUseCase,
)
from app.application.use_cases.user import (
    CleanupUnverifiedUsersUseCase,
    DeleteUserUseCase,
    GetAllUsersUseCase,
    UpdateUserUseCase,
)
from app.domain.entities import User, UserRole


# Test fixtures
@pytest.fixture
def mock_user_repo():
    """Create mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_password_service():
    """Create mock password service."""
    service = Mock()
    service.hash_password = Mock(return_value="hashed_password")
    service.verify_password = Mock(return_value=True)
    return service


@pytest.fixture
def mock_token_service():
    """Create mock token service."""
    service = Mock()
    service.create_access_token = Mock(return_value="access_token")
    service.create_refresh_token = Mock(return_value="refresh_token")
    service.verify_token = Mock(return_value={"sub": "1"})
    return service


@pytest.fixture
def mock_email_service():
    """Create mock email service."""
    return AsyncMock()


@pytest.fixture
def sample_user():
    """Create sample user entity."""
    return User(
        id=1,
        email="user@example.com",
        hashed_password="hashed_password",
        first_name="John",
        last_name="Doe",
        role=UserRole.USER,
        is_verified=True,
        verification_code=None,
        verification_code_expires_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_admin():
    """Create sample admin user entity."""
    return User(
        id=2,
        email="admin@example.com",
        hashed_password="hashed_password",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        is_verified=True,
        verification_code=None,
        verification_code_expires_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestSignupUseCase:
    """Test cases for SignupUseCase."""

    @pytest.mark.asyncio
    async def test_signup_creates_user_successfully(
        self, mock_user_repo, mock_password_service, mock_email_service
    ):
        """Test successful user signup."""
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.create.return_value = User(
            id=1,
            email="new@example.com",
            hashed_password="hashed_password",
            first_name="New",
            last_name="User",
            role=UserRole.USER,
            is_verified=False,
            verification_code="code123",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=48),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        use_case = SignupUseCase(
            mock_user_repo, mock_password_service, mock_email_service
        )

        request = SignupRequest(
            email="new@example.com",
            password="password123",
            first_name="New",
            last_name="User",
        )

        result = await use_case.execute(request)

        assert result.email == "new@example.com"
        assert result.is_verified is False
        mock_user_repo.exists_by_email.assert_called_once_with("new@example.com")
        mock_password_service.hash_password.assert_called_once_with("password123")
        mock_user_repo.create.assert_called_once()
        mock_email_service.send_verification_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_signup_raises_error_if_email_exists(
        self, mock_user_repo, mock_password_service, mock_email_service
    ):
        """Test signup raises error if email already exists."""
        mock_user_repo.exists_by_email.return_value = True

        use_case = SignupUseCase(
            mock_user_repo, mock_password_service, mock_email_service
        )

        request = SignupRequest(email="existing@example.com", password="password123")

        with pytest.raises(UserAlreadyExistsError):
            await use_case.execute(request)


class TestLoginUseCase:
    """Test cases for LoginUseCase."""

    @pytest.mark.asyncio
    async def test_login_returns_tokens_for_valid_credentials(
        self, mock_user_repo, mock_password_service, mock_token_service, sample_user
    ):
        """Test successful login with valid credentials."""
        mock_user_repo.get_by_email.return_value = sample_user

        use_case = LoginUseCase(
            mock_user_repo, mock_password_service, mock_token_service
        )

        request = LoginRequest(email="user@example.com", password="password123")

        result = await use_case.execute(request)

        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        assert result.token_type == "bearer"
        mock_password_service.verify_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_raises_error_for_nonexistent_user(
        self, mock_user_repo, mock_password_service, mock_token_service
    ):
        """Test login raises error if user doesn't exist."""
        mock_user_repo.get_by_email.return_value = None

        use_case = LoginUseCase(
            mock_user_repo, mock_password_service, mock_token_service
        )

        request = LoginRequest(email="nonexistent@example.com", password="password123")

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_login_raises_error_for_wrong_password(
        self, mock_user_repo, mock_password_service, mock_token_service, sample_user
    ):
        """Test login raises error for wrong password."""
        mock_user_repo.get_by_email.return_value = sample_user
        mock_password_service.verify_password.return_value = False

        use_case = LoginUseCase(
            mock_user_repo, mock_password_service, mock_token_service
        )

        request = LoginRequest(email="user@example.com", password="wrong_password")

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(request)


class TestVerifyEmailUseCase:
    """Test cases for VerifyEmailUseCase."""

    @pytest.mark.asyncio
    async def test_verify_email_successfully(self, mock_user_repo):
        """Test successful email verification."""
        unverified_user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_password",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
            is_verified=False,
            verification_code="code123",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        verified_user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_password",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
            is_verified=True,
            verification_code=None,
            verification_code_expires_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_user_repo.get_by_email.return_value = unverified_user
        mock_user_repo.update.return_value = verified_user

        use_case = VerifyEmailUseCase(mock_user_repo)

        request = VerifyRequest(email="user@example.com", verification_code="code123")

        result = await use_case.execute(request)

        assert result.is_verified is True
        mock_user_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email_raises_error_for_invalid_code(self, mock_user_repo):
        """Test verification raises error for invalid code."""
        unverified_user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_password",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
            is_verified=False,
            verification_code="correct_code",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_user_repo.get_by_email.return_value = unverified_user

        use_case = VerifyEmailUseCase(mock_user_repo)

        request = VerifyRequest(
            email="user@example.com", verification_code="wrong_code"
        )

        with pytest.raises(VerificationError):
            await use_case.execute(request)


class TestGetAllUsersUseCase:
    """Test cases for GetAllUsersUseCase."""

    @pytest.mark.asyncio
    async def test_get_all_users_as_admin(
        self, mock_user_repo, sample_admin, sample_user
    ):
        """Test admin can get all users."""
        mock_user_repo.get_by_id.return_value = sample_admin
        mock_user_repo.get_all.return_value = [sample_user, sample_admin]

        use_case = GetAllUsersUseCase(mock_user_repo)

        result = await use_case.execute(sample_admin.id)

        assert len(result) == 2
        mock_user_repo.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_users_raises_forbidden_for_regular_user(
        self, mock_user_repo, sample_user
    ):
        """Test regular user cannot get all users."""
        mock_user_repo.get_by_id.return_value = sample_user

        use_case = GetAllUsersUseCase(mock_user_repo)

        with pytest.raises(ForbiddenError):
            await use_case.execute(sample_user.id)


class TestUpdateUserUseCase:
    """Test cases for UpdateUserUseCase."""

    @pytest.mark.asyncio
    async def test_user_can_update_own_profile(self, mock_user_repo, sample_user):
        """Test user can update their own profile."""
        updated_user = User(
            id=sample_user.id,
            email=sample_user.email,
            hashed_password=sample_user.hashed_password,
            first_name="Updated",
            last_name="Name",
            role=sample_user.role,
            is_verified=sample_user.is_verified,
            verification_code=None,
            verification_code_expires_at=None,
            created_at=sample_user.created_at,
            updated_at=datetime.utcnow(),
        )

        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.update.return_value = updated_user

        use_case = UpdateUserUseCase(mock_user_repo)

        update_data = UpdateUserRequest(first_name="Updated", last_name="Name")

        result = await use_case.execute(sample_user.id, sample_user.id, update_data)

        assert result.first_name == "Updated"
        assert result.last_name == "Name"

    @pytest.mark.asyncio
    async def test_user_cannot_update_other_users(
        self, mock_user_repo, sample_user, sample_admin
    ):
        """Test regular user cannot update other users."""
        mock_user_repo.get_by_id.return_value = sample_user

        use_case = UpdateUserUseCase(mock_user_repo)

        update_data = UpdateUserRequest(first_name="Hacked")

        with pytest.raises(ForbiddenError):
            await use_case.execute(sample_user.id, sample_admin.id, update_data)


class TestDeleteUserUseCase:
    """Test cases for DeleteUserUseCase."""

    @pytest.mark.asyncio
    async def test_admin_can_delete_user(
        self, mock_user_repo, sample_admin, sample_user
    ):
        """Test admin can delete users."""
        mock_user_repo.get_by_id.side_effect = [sample_admin, sample_user]
        mock_user_repo.delete.return_value = True

        use_case = DeleteUserUseCase(mock_user_repo)

        result = await use_case.execute(sample_admin.id, sample_user.id)

        assert result is True
        mock_user_repo.delete.assert_called_once_with(sample_user.id)

    @pytest.mark.asyncio
    async def test_regular_user_cannot_delete_users(self, mock_user_repo, sample_user):
        """Test regular user cannot delete users."""
        mock_user_repo.get_by_id.return_value = sample_user

        use_case = DeleteUserUseCase(mock_user_repo)

        with pytest.raises(ForbiddenError):
            await use_case.execute(sample_user.id, 99)


class TestCleanupUnverifiedUsersUseCase:
    """Test cases for CleanupUnverifiedUsersUseCase."""

    @pytest.mark.asyncio
    async def test_cleanup_deletes_expired_unverified_users(self, mock_user_repo):
        """Test cleanup deletes expired unverified users."""
        expired_user = User(
            id=1,
            email="expired@example.com",
            hashed_password="hashed_password",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=False,
            verification_code="code",
            verification_code_expires_at=datetime.utcnow() - timedelta(hours=1),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_user_repo.get_unverified_expired.return_value = [expired_user]
        mock_user_repo.delete.return_value = True

        use_case = CleanupUnverifiedUsersUseCase(mock_user_repo)

        result = await use_case.execute()

        assert result == 1
        mock_user_repo.delete.assert_called_once_with(expired_user.id)
