"""
Integration tests for service implementations.
"""

import time

import pytest

from app.infrastructure.services.password_service import BcryptPasswordService
from app.infrastructure.services.token_service import JWTTokenService


class TestPasswordService:
    """Integration tests for BcryptPasswordService."""

    @pytest.fixture
    def password_service(self):
        """Create password service instance."""
        return BcryptPasswordService()

    def test_hash_password(self, password_service):
        """Test password hashing."""
        password = "mysecretpassword123"

        hashed = password_service.hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_produces_different_hashes(self, password_service):
        """Test that same password produces different hashes (salt)."""
        password = "samepassword"

        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2

    def test_verify_password_with_correct_password(self, password_service):
        """Test password verification with correct password."""
        password = "correctpassword"
        hashed = password_service.hash_password(password)

        result = password_service.verify_password(password, hashed)

        assert result is True

    def test_verify_password_with_wrong_password(self, password_service):
        """Test password verification with wrong password."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = password_service.hash_password(password)

        result = password_service.verify_password(wrong_password, hashed)

        assert result is False

    def test_verify_password_with_empty_password(self, password_service):
        """Test password verification with empty password."""
        password = "password123"
        hashed = password_service.hash_password(password)

        result = password_service.verify_password("", hashed)

        assert result is False


class TestTokenService:
    """Integration tests for JWTTokenService."""

    @pytest.fixture
    def token_service(self):
        """Create token service instance."""
        return JWTTokenService(
            secret_key="test-secret-key-for-testing",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

    def test_create_access_token(self, token_service):
        """Test creating access token."""
        user_id = 123

        token = token_service.create_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, token_service):
        """Test creating refresh token."""
        user_id = 456

        token = token_service.create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_access_token(self, token_service):
        """Test verifying valid access token."""
        user_id = 789
        token = token_service.create_access_token(user_id)

        payload = token_service.verify_token(token)

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_verify_valid_refresh_token(self, token_service):
        """Test verifying valid refresh token."""
        user_id = 101112
        token = token_service.create_refresh_token(user_id)

        payload = token_service.verify_token(token)

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_verify_invalid_token(self, token_service):
        """Test verifying invalid token."""
        invalid_token = "invalid.token.here"

        with pytest.raises(Exception):
            token_service.verify_token(invalid_token)

    def test_verify_token_with_wrong_secret(self, token_service):
        """Test verifying token with wrong secret key."""
        user_id = 131415
        token = token_service.create_access_token(user_id)

        # Create service with different secret
        wrong_service = JWTTokenService(
            secret_key="wrong-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

        with pytest.raises(Exception):
            wrong_service.verify_token(token)

    def test_token_contains_expiration(self, token_service):
        """Test that token contains expiration timestamp."""
        user_id = 161718
        token = token_service.create_access_token(user_id)

        payload = token_service.verify_token(token)

        assert "exp" in payload
        assert payload["exp"] is not None

    def test_different_tokens_for_same_user(self, token_service):
        """Test that different tokens are generated for same user."""
        user_id = 192021

        token1 = token_service.create_access_token(user_id)
        time.sleep(1)  # Ensure different timestamp
        token2 = token_service.create_access_token(user_id)

        # Tokens should be different due to different timestamps
        assert token1 != token2

    def test_access_and_refresh_tokens_are_different(self, token_service):
        """Test that access and refresh tokens are different."""
        user_id = 222324

        access_token = token_service.create_access_token(user_id)
        refresh_token = token_service.create_refresh_token(user_id)

        assert access_token != refresh_token

        access_payload = token_service.verify_token(access_token)
        refresh_payload = token_service.verify_token(refresh_token)

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"

        # Refresh token should have longer expiration
        assert refresh_payload["exp"] > access_payload["exp"]
