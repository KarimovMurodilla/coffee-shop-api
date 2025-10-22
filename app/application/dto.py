from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.domain.entities import User, UserRole

# Request DTOs


class SignupRequest(BaseModel):
    """
    Data transfer object for user signup request.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ..., min_length=8, description="User's password (minimum 8 characters)"
    )
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")


class LoginRequest(BaseModel):
    """
    Data transfer object for user login request.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class VerifyRequest(BaseModel):
    """
    Data transfer object for email verification request.
    """

    email: EmailStr = Field(..., description="User's email address")
    verification_code: str = Field(..., description="Verification code sent to email")


class RefreshTokenRequest(BaseModel):
    """
    Data transfer object for token refresh request.
    """

    refresh_token: str = Field(..., description="Valid refresh token")


class UpdateUserRequest(BaseModel):
    """
    Data transfer object for updating user information.
    All fields are optional for partial updates.
    """

    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")


# Response DTOs


class TokenResponse(BaseModel):
    """
    Data transfer object for token response.
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """
    Data transfer object for user response.
    """

    id: int = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    role: UserRole = Field(..., description="User's role")
    is_verified: bool = Field(..., description="Whether user's email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        """
        Create UserResponse from User entity.
        """
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class MessageResponse(BaseModel):
    """
    Generic message response.
    """

    message: str = Field(..., description="Response message")
