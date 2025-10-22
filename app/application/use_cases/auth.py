import secrets
from datetime import datetime, timedelta

from app.application.dto import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
    VerifyRequest,
)
from app.application.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    VerificationError,
)
from app.domain.entities import User, UserRole
from app.domain.repositories import UserRepository
from app.domain.services import EmailService, PasswordService, TokenService


class SignupUseCase:
    """
    Use case for user registration.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordService,
        email_service: EmailService,
        verification_expire_hours: int = 48,
    ):
        self.user_repo = user_repo
        self.password_service = password_service
        self.email_service = email_service
        self.verification_expire_hours = verification_expire_hours

    async def execute(self, request: SignupRequest) -> UserResponse:
        """
        Register a new user.

        Args:
            request: Signup request data

        Returns:
            UserResponse with created user data

        Raises:
            UserAlreadyExistsError: If email is already registered
        """
        # Check if user already exists
        if await self.user_repo.exists_by_email(request.email):
            raise UserAlreadyExistsError(
                f"User with email {request.email} already exists"
            )

        # Generate verification code
        verification_code = secrets.token_urlsafe(32)
        verification_expires_at = datetime.utcnow() + timedelta(
            hours=self.verification_expire_hours
        )

        # Create user entity
        user = User(
            id=None,
            email=request.email,
            hashed_password=self.password_service.hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            role=UserRole.USER,
            is_verified=False,
            verification_code=verification_code,
            verification_code_expires_at=verification_expires_at,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save user
        created_user = await self.user_repo.create(user)

        # Send verification email (async, don't wait for result)
        # In production, this should be handled by a background task
        try:
            await self.email_service.send_verification_email(
                created_user.email, verification_code
            )
        except Exception as e:
            # Log error but don't fail registration
            print(f"Failed to send verification email: {e}")

        return UserResponse.from_entity(created_user)


class LoginUseCase:
    """
    Use case for user authentication.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ):
        self.user_repo = user_repo
        self.password_service = password_service
        self.token_service = token_service

    async def execute(self, request: LoginRequest) -> TokenResponse:
        """
        Authenticate user and issue tokens.

        Args:
            request: Login request data

        Returns:
            TokenResponse with access and refresh tokens

        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repo.get_by_email(request.email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        # Verify password
        if not self.password_service.verify_password(
            request.password, user.hashed_password
        ):
            raise InvalidCredentialsError("Invalid email or password")

        # Generate tokens
        access_token = self.token_service.create_access_token(user.id)
        refresh_token = self.token_service.create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )


class RefreshTokenUseCase:
    """
    Use case for refreshing access token.
    """

    def __init__(self, user_repo: UserRepository, token_service: TokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    async def execute(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            TokenResponse with new access token

        Raises:
            InvalidCredentialsError: If refresh token is invalid
        """
        try:
            payload = self.token_service.verify_token(refresh_token)
            user_id = payload.get("sub")

            if not user_id:
                raise InvalidCredentialsError("Invalid token")

            # Verify user still exists
            user = await self.user_repo.get_by_id(int(user_id))
            if not user:
                raise InvalidCredentialsError("User not found")

            # Generate new access token
            new_access_token = self.token_service.create_access_token(user.id)

            return TokenResponse(
                access_token=new_access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
        except Exception:
            raise InvalidCredentialsError("Invalid or expired token")


class VerifyEmailUseCase:
    """
    Use case for email verification.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, request: VerifyRequest) -> UserResponse:
        """
        Verify user's email using verification code.

        Args:
            request: Verification request data

        Returns:
            UserResponse with updated user data

        Raises:
            UserNotFoundError: If user not found
            VerificationError: If verification code is invalid or expired
        """
        # Get user by email
        user = await self.user_repo.get_by_email(request.email)
        if not user:
            raise UserNotFoundError(f"User with email {request.email} not found")

        # Check if already verified
        if user.is_verified:
            raise VerificationError("User is already verified")

        # Verify code
        if not user.can_verify(request.verification_code):
            raise VerificationError("Invalid or expired verification code")

        # Mark as verified
        user.verify()
        user.updated_at = datetime.utcnow()

        # Update in database
        updated_user = await self.user_repo.update(user)

        return UserResponse.from_entity(updated_user)
