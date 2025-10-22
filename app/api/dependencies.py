from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.entities import User
from app.infrastructure.database.connection import get_db_session
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.services.email_service import MailJetEmailService
from app.infrastructure.services.password_service import BcryptPasswordService
from app.infrastructure.services.token_service import JWTTokenService

security = HTTPBearer()


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyUserRepository:
    """
    Dependency for getting user repository.
    """
    return SQLAlchemyUserRepository(session)


def get_password_service() -> BcryptPasswordService:
    """
    Dependency for getting password service.
    """
    return BcryptPasswordService()


def get_token_service() -> JWTTokenService:
    """
    Dependency for getting token service.
    """
    return JWTTokenService(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def get_email_service() -> MailJetEmailService:
    """
    Dependency for getting email service.
    """
    return MailJetEmailService(
        api_key=settings.mailjet_api_key,
        api_secret=settings.mailjet_api_secret,
        from_email=settings.mailjet_from_email,
        from_name=settings.mailjet_from_name,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_service: JWTTokenService = Depends(get_token_service),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> User:
    """
    Dependency for getting current authenticated user from JWT token.

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        payload = token_service.verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        user = await user_repo.get_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency for getting current authenticated admin user.

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
