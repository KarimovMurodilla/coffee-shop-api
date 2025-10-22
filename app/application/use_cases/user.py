from datetime import datetime
from typing import List

from app.application.dto import UpdateUserRequest, UserResponse
from app.application.exceptions import ForbiddenError, UserNotFoundError
from app.domain.repositories import UserRepository


class GetCurrentUserUseCase:
    """
    Use case for retrieving current authenticated user.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, user_id: int) -> UserResponse:
        """
        Get current user by ID.

        Args:
            user_id: ID of the authenticated user

        Returns:
            UserResponse with user data

        Raises:
            UserNotFoundError: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        return UserResponse.from_entity(user)


class GetAllUsersUseCase:
    """
    Use case for retrieving all users (admin only).
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(
        self, requesting_user_id: int, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """
        Get all users with pagination.

        Args:
            requesting_user_id: ID of the user making the request
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of UserResponse objects

        Raises:
            ForbiddenError: If requesting user is not admin
        """
        # Check if user is admin
        requesting_user = await self.user_repo.get_by_id(requesting_user_id)
        if not requesting_user or not requesting_user.is_admin():
            raise ForbiddenError("Only admins can access this resource")

        users = await self.user_repo.get_all(skip=skip, limit=limit)
        return [UserResponse.from_entity(user) for user in users]


class GetUserByIdUseCase:
    """
    Use case for retrieving user by ID (admin only).
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(
        self, requesting_user_id: int, target_user_id: int
    ) -> UserResponse:
        """
        Get user by ID.

        Args:
            requesting_user_id: ID of the user making the request
            target_user_id: ID of the user to retrieve

        Returns:
            UserResponse with user data

        Raises:
            ForbiddenError: If requesting user is not admin
            UserNotFoundError: If target user not found
        """
        # Check if user is admin
        requesting_user = await self.user_repo.get_by_id(requesting_user_id)
        if not requesting_user or not requesting_user.is_admin():
            raise ForbiddenError("Only admins can access this resource")

        user = await self.user_repo.get_by_id(target_user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {target_user_id} not found")

        return UserResponse.from_entity(user)


class UpdateUserUseCase:
    """
    Use case for updating user information.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(
        self,
        requesting_user_id: int,
        target_user_id: int,
        update_data: UpdateUserRequest,
    ) -> UserResponse:
        """
        Update user information.
        Users can update their own info, admins can update any user.

        Args:
            requesting_user_id: ID of the user making the request
            target_user_id: ID of the user to update
            update_data: Data to update

        Returns:
            UserResponse with updated user data

        Raises:
            ForbiddenError: If user doesn't have permission
            UserNotFoundError: If target user not found
        """
        # Get requesting user
        requesting_user = await self.user_repo.get_by_id(requesting_user_id)
        if not requesting_user:
            raise UserNotFoundError(
                f"Requesting user with ID {requesting_user_id} not found"
            )

        # Check permissions: user can update themselves, admin can update anyone
        if requesting_user_id != target_user_id and not requesting_user.is_admin():
            raise ForbiddenError("You don't have permission to update this user")

        # Get target user
        user = await self.user_repo.get_by_id(target_user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {target_user_id} not found")

        # Update fields if provided
        if update_data.first_name is not None:
            user.first_name = update_data.first_name

        if update_data.last_name is not None:
            user.last_name = update_data.last_name

        user.updated_at = datetime.utcnow()

        # Save changes
        updated_user = await self.user_repo.update(user)

        return UserResponse.from_entity(updated_user)


class DeleteUserUseCase:
    """
    Use case for deleting user (admin only).
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, requesting_user_id: int, target_user_id: int) -> bool:
        """
        Delete user by ID.

        Args:
            requesting_user_id: ID of the user making the request
            target_user_id: ID of the user to delete

        Returns:
            True if deleted successfully

        Raises:
            ForbiddenError: If requesting user is not admin
            UserNotFoundError: If target user not found
        """
        # Check if user is admin
        requesting_user = await self.user_repo.get_by_id(requesting_user_id)
        if not requesting_user or not requesting_user.is_admin():
            raise ForbiddenError("Only admins can delete users")

        # Check if target user exists
        user = await self.user_repo.get_by_id(target_user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {target_user_id} not found")

        # Delete user
        return await self.user_repo.delete(target_user_id)


class CleanupUnverifiedUsersUseCase:
    """
    Use case for cleaning up unverified users (used by Celery task).
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self) -> int:
        """
        Delete all unverified users whose verification has expired.

        Returns:
            Number of deleted users
        """
        expired_users = await self.user_repo.get_unverified_expired()
        deleted_count = 0

        for user in expired_users:
            if user.should_be_deleted():
                await self.user_repo.delete(user.id)
                deleted_count += 1

        return deleted_count, expired_users
