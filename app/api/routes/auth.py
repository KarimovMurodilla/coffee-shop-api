from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_email_service,
    get_password_service,
    get_token_service,
    get_user_repository,
)
from app.application.dto import (
    LoginRequest,
    RefreshTokenRequest,
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
from app.application.use_cases.auth import (
    LoginUseCase,
    RefreshTokenUseCase,
    SignupUseCase,
    VerifyEmailUseCase,
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Email must be unique. "
    "User will receive a verification code via email.",
)
async def signup(
    request: SignupRequest,
    user_repo=Depends(get_user_repository),
    password_service=Depends(get_password_service),
    email_service=Depends(get_email_service),
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Password with minimum 8 characters
    - **first_name**: Optional first name
    - **last_name**: Optional last name

    Returns the created user information (excluding password).
    A verification code will be sent to the provided email.
    """
    use_case = SignupUseCase(
        user_repo,
        password_service,
        email_service,
        settings.verification_code_expire_hours,
    )

    try:
        return await use_case.execute(request)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and receive access and refresh tokens.",
)
async def login(
    request: LoginRequest,
    user_repo=Depends(get_user_repository),
    password_service=Depends(get_password_service),
    token_service=Depends(get_token_service),
):
    """
    Authenticate user and return JWT tokens.

    - **email**: User's email address
    - **password**: User's password

    Returns access and refresh tokens for authenticated requests.
    """
    use_case = LoginUseCase(user_repo, password_service, token_service)

    try:
        return await use_case.execute(request)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    user_repo=Depends(get_user_repository),
    token_service=Depends(get_token_service),
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token

    Returns a new access token while keeping the same refresh token.
    """
    use_case = RefreshTokenUseCase(user_repo, token_service)

    try:
        return await use_case.execute(request.refresh_token)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/verify",
    response_model=UserResponse,
    summary="Verify email address",
    description="Verify user's email address using "
    "the verification code sent during registration.",
)
async def verify_email(request: VerifyRequest, user_repo=Depends(get_user_repository)):
    """
    Verify user's email address.

    - **email**: User's email address
    - **verification_code**: Verification code received via email

    Returns the updated user information with verified status.
    """
    use_case = VerifyEmailUseCase(user_repo)

    try:
        return await use_case.execute(request)
    except (UserNotFoundError, VerificationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
