"""
Unit tests for domain entities.
"""

from datetime import datetime, timedelta

from app.domain.entities import User, UserRole


class TestUser:
    """Test cases for User entity."""

    def test_user_creation(self):
        """Test creating a user entity."""
        user = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_pass",
            first_name="John",
            last_name="Doe",
            role=UserRole.USER,
            is_verified=False,
            verification_code="code123",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=48),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.is_verified is False

    def test_is_admin_returns_true_for_admin_role(self):
        """Test is_admin() returns True for admin users."""
        user = User(
            id=1,
            email="admin@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.ADMIN,
            is_verified=True,
            verification_code=None,
            verification_code_expires_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.is_admin() is True

    def test_is_admin_returns_false_for_regular_user(self):
        """Test is_admin() returns False for regular users."""
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=True,
            verification_code=None,
            verification_code_expires_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.is_admin() is False

    def test_can_verify_returns_true_for_valid_code(self):
        """Test can_verify() returns True for valid verification code."""
        verification_code = "valid_code_123"
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=False,
            verification_code=verification_code,
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.can_verify(verification_code) is True

    def test_can_verify_returns_false_for_invalid_code(self):
        """Test can_verify() returns False for invalid verification code."""
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=False,
            verification_code="valid_code",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.can_verify("wrong_code") is False

    def test_can_verify_returns_false_for_expired_code(self):
        """Test can_verify() returns False for expired verification code."""
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=False,
            verification_code="valid_code",
            verification_code_expires_at=datetime.utcnow() - timedelta(hours=1),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.can_verify("valid_code") is False

    def test_can_verify_returns_false_for_already_verified_user(self):
        """Test can_verify() returns False if user is already verified."""
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=True,
            verification_code="code",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.can_verify("code") is False

    def test_verify_marks_user_as_verified(self):
        """Test verify() marks user as verified and clears verification data."""
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=False,
            verification_code="code123",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        user.verify()

        assert user.is_verified is True
        assert user.verification_code is None
        assert user.verification_code_expires_at is None

    def test_should_be_deleted_returns_true_for_expired_unverified_user(self):
        """Test should_be_deleted() returns True for expired unverified users."""
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=False,
            verification_code="code",
            verification_code_expires_at=datetime.utcnow() - timedelta(hours=1),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.should_be_deleted() is True

    def test_should_be_deleted_returns_false_for_verified_user(self):
        """Test should_be_deleted() returns False for verified users."""
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=True,
            verification_code=None,
            verification_code_expires_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.should_be_deleted() is False

    def test_should_be_deleted_returns_false_for_unverified_not_expired(self):
        """
        Test should_be_deleted()
        returns False for unverified
        users with valid code.
        """
        user = User(
            id=1,
            email="user@example.com",
            hashed_password="hashed_pass",
            first_name=None,
            last_name=None,
            role=UserRole.USER,
            is_verified=False,
            verification_code="code",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert user.should_be_deleted() is False


class TestUserRole:
    """Test cases for UserRole enum."""

    def test_user_role_enum_values(self):
        """Test UserRole enum has correct values."""
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"

    def test_user_role_comparison(self):
        """Test UserRole enum comparison."""
        assert UserRole.USER == UserRole.USER
        assert UserRole.ADMIN == UserRole.ADMIN
        assert UserRole.USER != UserRole.ADMIN
