import pytest
from fastapi import status

from app.core.exceptions import AuthExceptions, UserExceptions


class TestExceptions:
    """Test custom exception classes."""

    def test_auth_exceptions_invalid_credentials(self):
        """Test AuthExceptions.invalid_credentials."""
        exc = AuthExceptions.invalid_credentials()

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in exc.detail
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_auth_exceptions_invalid_token(self):
        """Test AuthExceptions.invalid_token."""
        exc = AuthExceptions.invalid_token()

        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or expired access token" in exc.detail
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_user_exceptions_email_already_registered(self):
        """Test UserExceptions.email_already_registered."""
        exc = UserExceptions.email_already_registered()

        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in exc.detail

    def test_user_exceptions_user_not_found(self):
        """Test UserExceptions.user_not_found."""
        exc = UserExceptions.user_not_found()

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc.detail
