from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.domain.repositories import UserRepository
from app.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """
    SQLAlchemy implementation of UserRepository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            first_name=model.first_name,
            last_name=model.last_name,
            role=model.role,
            is_verified=model.is_verified,
            verification_code=model.verification_code,
            verification_code_expires_at=model.verification_code_expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to database model."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role,
            is_verified=entity.is_verified,
            verification_code=entity.verification_code,
            verification_code_expires_at=entity.verification_code_expires_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, user: User) -> User:
        """Create a new user."""
        model = self._to_model(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        result = await self.session.execute(select(UserModel).offset(skip).limit(limit))
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, user: User) -> User:
        """Update user information."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one_or_none()

        if model:
            model.email = user.email
            model.hashed_password = user.hashed_password
            model.first_name = user.first_name
            model.last_name = user.last_name
            model.role = user.role
            model.is_verified = user.is_verified
            model.verification_code = user.verification_code
            model.verification_code_expires_at = user.verification_code_expires_at
            model.updated_at = user.updated_at

            await self.session.commit()
            await self.session.refresh(model)
            return self._to_entity(model)

        return user

    async def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True

        return False

    async def get_unverified_expired(self) -> List[User]:
        """Get all unverified users whose verification has expired."""
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.is_verified == False,
                UserModel.verification_code_expires_at < datetime.utcnow(),
            )
        )
        models = result.scalars().all()
        users = [self._to_entity(model) for model in models]
        users2 = [self._to_entity(model).verification_code_expires_at for model in models]
        print(f"{users2=}") 
        return users

    async def exists_by_email(self, email: str) -> bool:
        """Check if user with given email exists."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None
