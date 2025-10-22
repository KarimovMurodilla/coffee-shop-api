from abc import ABC, abstractmethod


class EmailService(ABC):
    """
    Abstract interface for email sending service.
    """

    @abstractmethod
    async def send_verification_email(
        self, to_email: str, verification_code: str
    ) -> bool:
        """
        Send verification email to user.

        Args:
            to_email: Recipient email address
            verification_code: Verification code to include in email

        Returns:
            True if email was sent successfully, False otherwise
        """
        pass


class PasswordService(ABC):
    """
    Abstract interface for password hashing and verification.
    """

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a plain text password."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        pass


class TokenService(ABC):
    """
    Abstract interface for JWT token generation and validation.
    """

    @abstractmethod
    def create_access_token(self, user_id: int) -> str:
        """Create access token for user."""
        pass

    @abstractmethod
    def create_refresh_token(self, user_id: int) -> str:
        """Create refresh token for user."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict:
        """
        Verify and decode token.

        Returns:
            Dictionary containing token payload

        Raises:
            Exception if token is invalid or expired
        """
        pass
