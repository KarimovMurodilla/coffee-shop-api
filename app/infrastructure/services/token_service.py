from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.domain.services import TokenService


class JWTTokenService(TokenService):
    """
    JWT token service for creating and verifying tokens.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_days: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, user_id: int) -> str:
        """
        Create JWT access token for user.

        Args:
            user_id: User's unique identifier

        Returns:
            JWT access token
        """
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {"sub": str(user_id), "exp": expire, "type": "access"}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: int) -> str:
        """
        Create JWT refresh token for user.

        Args:
            user_id: User's unique identifier

        Returns:
            JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Dictionary containing token payload

        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise Exception(f"Invalid token: {str(e)}")
