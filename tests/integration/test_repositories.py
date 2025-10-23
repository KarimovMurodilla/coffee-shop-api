"""
Integration tests for repository implementations.
These tests use a real database connection (test database).
"""

from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.entities import User, UserRole
from app.infrastructure.database.models import Base
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

# Test database URL (use SQLite for tests)
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
async def test_session(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def user_repository(test_session):
    """Create user repository with test session."""
    return SQLAlchemyUserRepository(test_session)


@pytest.fixture
def sample_user_entity():
    """Create sample user entity for testing."""
    return User(
        id=None,
        email="test@example.com",
        hashed_password="hashed_password_123",
        first_name="John",
        last_name="Doe",
        role=UserRole.USER,
        is_verified=False,
        verification_code="code123",
        verification_code_expires_at=datetime.utcnow() + timedelta(hours=48),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestUserRepository:
    """Integration tests for UserRepository."""

    @pytest.mark.asyncio
    async def test_create_user(self, user_repository, sample_user_entity):
        """Test creating a new user."""
        created_user = await user_repository.create(sample_user_entity)

        assert created_user.id is not None
        assert created_user.email == "test@example.com"
        assert created_user.role == UserRole.USER
        assert created_user.is_verified is False

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_repository, sample_user_entity):
        """Test retrieving user by ID."""
        created_user = await user_repository.create(sample_user_entity)

        retrieved_user = await user_repository.get_by_id(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_returns_none_for_nonexistent(self, user_repository):
        """Test get_by_id returns None for non-existent user."""
        user = await user_repository.get_by_id(99999)

        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_repository, sample_user_entity):
        """Test retrieving user by email."""
        created_user = await user_repository.create(sample_user_entity)

        retrieved_user = await user_repository.get_by_email(created_user.email)

        assert retrieved_user is not None
        assert retrieved_user.email == created_user.email
        assert retrieved_user.id == created_user.id

    @pytest.mark.asyncio
    async def test_get_user_by_email_returns_none_for_nonexistent(
        self, user_repository
    ):
        """Test get_by_email returns None for non-existent email."""
        user = await user_repository.get_by_email("nonexistent@example.com")

        assert user is None

    @pytest.mark.asyncio
    async def test_exists_by_email(self, user_repository, sample_user_entity):
        """Test checking if user exists by email."""
        await user_repository.create(sample_user_entity)

        exists = await user_repository.exists_by_email("test@example.com")
        assert exists is True

        not_exists = await user_repository.exists_by_email("other@example.com")
        assert not_exists is False

    @pytest.mark.asyncio
    async def test_get_all_users(self, user_repository):
        """Test retrieving all users."""
        # Create multiple users
        for i in range(3):
            user = User(
                id=None,
                email=f"user{i}@example.com",
                hashed_password="hashed",
                first_name=f"User{i}",
                last_name="Test",
                role=UserRole.USER,
                is_verified=False,
                verification_code=f"code{i}",
                verification_code_expires_at=datetime.utcnow() + timedelta(hours=48),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            await user_repository.create(user)

        all_users = await user_repository.get_all()

        assert len(all_users) == 3

    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination(self, user_repository):
        """Test retrieving users with pagination."""
        # Create 5 users
        for i in range(5):
            user = User(
                id=None,
                email=f"user{i}@example.com",
                hashed_password="hashed",
                first_name=f"User{i}",
                last_name="Test",
                role=UserRole.USER,
                is_verified=False,
                verification_code=f"code{i}",
                verification_code_expires_at=datetime.utcnow() + timedelta(hours=48),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            await user_repository.create(user)

        # Test pagination
        first_page = await user_repository.get_all(skip=0, limit=2)
        assert len(first_page) == 2

        second_page = await user_repository.get_all(skip=2, limit=2)
        assert len(second_page) == 2

        third_page = await user_repository.get_all(skip=4, limit=2)
        assert len(third_page) == 1

    @pytest.mark.asyncio
    async def test_update_user(self, user_repository, sample_user_entity):
        """Test updating user information."""
        created_user = await user_repository.create(sample_user_entity)

        # Modify user
        created_user.first_name = "Jane"
        created_user.last_name = "Smith"
        created_user.is_verified = True
        created_user.verification_code = None

        updated_user = await user_repository.update(created_user)

        assert updated_user.first_name == "Jane"
        assert updated_user.last_name == "Smith"
        assert updated_user.is_verified is True
        assert updated_user.verification_code is None

        # Verify changes persisted
        retrieved_user = await user_repository.get_by_id(created_user.id)
        assert retrieved_user.first_name == "Jane"
        assert retrieved_user.is_verified is True

    @pytest.mark.asyncio
    async def test_delete_user(self, user_repository, sample_user_entity):
        """Test deleting a user."""
        created_user = await user_repository.create(sample_user_entity)
        user_id = created_user.id

        # Delete user
        result = await user_repository.delete(user_id)
        assert result is True

        # Verify user is deleted
        deleted_user = await user_repository.get_by_id(user_id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, user_repository):
        """Test deleting non-existent user returns False."""
        result = await user_repository.delete(99999)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_unverified_expired_users(self, user_repository):
        """Test retrieving unverified expired users."""
        # Create expired unverified user
        expired_user = User(
            id=None,
            email="expired@example.com",
            hashed_password="hashed",
            first_name="Expired",
            last_name="User",
            role=UserRole.USER,
            is_verified=False,
            verification_code="code",
            verification_code_expires_at=datetime.utcnow() - timedelta(hours=1),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await user_repository.create(expired_user)

        # Create valid unverified user
        valid_user = User(
            id=None,
            email="valid@example.com",
            hashed_password="hashed",
            first_name="Valid",
            last_name="User",
            role=UserRole.USER,
            is_verified=False,
            verification_code="code2",
            verification_code_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await user_repository.create(valid_user)

        # Create verified user
        verified_user = User(
            id=None,
            email="verified@example.com",
            hashed_password="hashed",
            first_name="Verified",
            last_name="User",
            role=UserRole.USER,
            is_verified=True,
            verification_code=None,
            verification_code_expires_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await user_repository.create(verified_user)

        # Get expired unverified users
        expired_users = await user_repository.get_unverified_expired()

        assert len(expired_users) == 1
        assert expired_users[0].email == "expired@example.com"
