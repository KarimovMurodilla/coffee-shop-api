from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    """
    User roles enumeration.
    """

    USER = "user"
    ADMIN = "admin"


class User:
    """
    User domain entity representing a user in the system.
    This is the core business object independent of any infrastructure concerns.
    """

    def __init__(
        self,
        id: Optional[int],
        email: str,
        hashed_password: str,
        first_name: Optional[str],
        last_name: Optional[str],
        role: UserRole,
        is_verified: bool,
        verification_code: Optional[str],
        verification_code_expires_at: Optional[datetime],
        created_at: datetime,
        updated_at: datetime,
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.is_verified = is_verified
        self.verification_code = verification_code
        self.verification_code_expires_at = verification_code_expires_at
        self.created_at = created_at
        self.updated_at = updated_at

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN

    def can_verify(self, code: str) -> bool:
        """
        Check if the provided verification code is valid and not expired.
        """
        if not self.verification_code or not self.verification_code_expires_at:
            return False

        if self.is_verified:
            return False

        if datetime.utcnow() > self.verification_code_expires_at:
            return False

        return self.verification_code == code

    def verify(self) -> None:
        """Mark user as verified."""
        self.is_verified = True
        self.verification_code = None
        self.verification_code_expires_at = None

    def should_be_deleted(self) -> bool:
        """
        Check if unverified user should be deleted (after 2 days).
        """
        if self.is_verified:
            return False

        if not self.verification_code_expires_at:
            return False

        return datetime.utcnow() > self.verification_code_expires_at
