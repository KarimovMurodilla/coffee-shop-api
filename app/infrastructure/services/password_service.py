from passlib.context import CryptContext

from app.domain.services import PasswordService


class BcryptPasswordService(PasswordService):
    """
    Password hashing service using
    bcrypt with SHA-256 pre-hash to avoid the 72-byte limit.
    Uses the passlib 'bcrypt_sha256' scheme which
    applies a SHA-256 pre-hash before bcrypt.
    """

    def __init__(self):
        # use bcrypt_sha256 to prevent "password cannot be longer than 72 bytes" errors
        self.pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password using bcrypt_sha256.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """

        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
