from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_user_repository,
)
from app.application.dto import MessageResponse, UpdateUserRequest, UserResponse
from app.application.exceptions import ForbiddenError, UserNotFoundError
from app.application.use_cases.user import (
    DeleteUserUseCase,
    GetAllUsersUseCase,
    GetCurrentUserUseCase,
    GetUserByIdUseCase,
    UpdateUserUseCase,
)
from app.domain.entities import User


import asyncio

from app.application.use_cases.user import CleanupUnverifiedUsersUseCase
from app.infrastructure.database.connection import AsyncSessionLocal
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve information about the currently authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
    user_repo=Depends(get_user_repository),
):
    """
    Get current authenticated user's information.

    Requires: Valid access token

    Returns the current user's profile information.
    """
    use_case = GetCurrentUserUseCase(user_repo)

    try: 
        return await use_case.execute(current_user.id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Get all users (Admin only)",
    description="Retrieve a list of all users with pagination. "
    "Only accessible by administrators.",
)
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of records to return"
    ),
    current_user: User = Depends(get_current_admin_user),
    user_repo=Depends(get_user_repository),
):
    """
    Get all users with pagination.

    Requires: Admin role

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 500)

    Returns a list of users.
    """
    use_case = GetAllUsersUseCase(user_repo)

    try:
        return await use_case.execute(current_user.id, skip, limit)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID (Admin only)",
    description="Retrieve information about a specific user by ID. "
    "Only accessible by administrators.",
)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    user_repo=Depends(get_user_repository),
):
    """
    Get user by ID.

    Requires: Admin role

    - **user_id**: ID of the user to retrieve

    Returns the user's information.
    """
    use_case = GetUserByIdUseCase(user_repo)

    try:
        return await use_case.execute(current_user.id, user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user information",
    description="Update user information. Users can update their own information, "
    "admins can update any user.",
)
async def update_user(
    user_id: int,
    update_data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    user_repo=Depends(get_user_repository),
):
    """
    Update user information (partial update).

    Requires: Valid access token (own user or admin)

    - **user_id**: ID of the user to update
    - **first_name**: New first name (optional)
    - **last_name**: New last name (optional)

    Users can only update their own information unless they are admins.
    Returns the updated user information.
    """
    use_case = UpdateUserUseCase(user_repo)

    try:
        return await use_case.execute(current_user.id, user_id, update_data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user (Admin only)",
    description="Delete a user by ID. Only accessible by administrators.",
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    user_repo=Depends(get_user_repository),
):
    """
    Delete user by ID.

    Requires: Admin role

    - **user_id**: ID of the user to delete

    Returns a success message upon deletion.
    """
    use_case = DeleteUserUseCase(user_repo)

    try:
        await use_case.execute(current_user.id, user_id)
        return MessageResponse(message=f"User {user_id} deleted successfully")
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
