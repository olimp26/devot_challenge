from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)

settings = get_settings()


class TestSecurity:
    """Test security functions."""

    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50  # Hashed password should be longer
        assert hashed.startswith("$2b$")  # bcrypt format

    def test_password_verification_correct(self):
        """Test password verification with correct password."""
        password = "correctpassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_incorrect(self):
        """Test password verification with incorrect password."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_password_hash_uniqueness(self):
        """Test that same password generates different hashes."""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # Due to salt, hashes should be different
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token_default_expiration(self):
        """Test creating access token with default expiration."""
        email = "test@example.com"
        token = create_access_token(subject=email)

        assert isinstance(token, str)

        # Decode and verify payload
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == email
        assert "exp" in payload

    def test_verify_token_valid(self):
        """Test verifying a valid token."""
        email = "valid@example.com"
        token = create_access_token(subject=email)

        verified_email = verify_token(token)
        assert verified_email == email

    def test_verify_token_invalid_signature(self):
        """Test verifying token with invalid signature."""
        email = "test@example.com"
        token = create_access_token(subject=email)

        invalid_token = token[:-1] + "X"

        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        assert exc_info.value.status_code == 401
        assert "Invalid or expired access token" in str(exc_info.value.detail)

    def test_verify_token_expired(self):
        """Test verifying an expired token."""
        email = "expired@example.com"
        past_expiration = timedelta(minutes=-10)
        token = create_access_token(
            subject=email, expires_delta=past_expiration)

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 401
        assert "Invalid or expired access token" in str(exc_info.value.detail)

    def test_verify_token_invalid_format(self):
        """Test verifying token with invalid format."""
        invalid_tokens = [
            "not.a.jwt",
            "totally_invalid_string",
            "",
            None
        ]

        for invalid_token in invalid_tokens:
            with pytest.raises(HTTPException) as exc_info:
                verify_token(invalid_token)
            assert exc_info.value.status_code == 401
            assert "Invalid or expired access token" in str(
                exc_info.value.detail)

    def test_verify_token_wrong_algorithm(self):
        """Test verifying token created with wrong algorithm."""
        email = "test@example.com"
        payload = {
            "sub": email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
        }

        # Create token with different algorithm
        wrong_algorithm_token = jwt.encode(
            payload, settings.secret_key, algorithm="HS512")

        with pytest.raises(HTTPException) as exc_info:
            verify_token(wrong_algorithm_token)
        assert exc_info.value.status_code == 401
        assert "Invalid or expired access token" in str(exc_info.value.detail)

    def test_create_token_with_numeric_subject(self):
        """Test creating token with numeric subject (user ID)."""
        user_id = 12345
        token = create_access_token(subject=user_id)

        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == str(user_id)  # Should be converted to string
