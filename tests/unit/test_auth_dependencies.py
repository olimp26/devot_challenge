import pytest
from fastapi import HTTPException

from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_token
from app.crud.user import get_user_by_email


class TestAuthenticationDependencies:
    """Test authentication dependency functions."""

    def test_get_current_user_success(self, db_session, sample_user):
        """Test getting current user with valid email."""
        user = get_current_user(db_session, sample_user.email)
        assert user is not None
        assert user.email == sample_user.email
        assert user.id == sample_user.id

    def test_get_current_user_not_found(self, db_session):
        """Test getting current user when user doesn't exist in database."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(db_session, "nonexistent@example.com")

        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    def test_full_authentication_chain(self, db_session, sample_user):
        """Test the complete authentication dependency chain."""
        token = create_access_token(subject=sample_user.email)

        verified_email = verify_token(token)
        assert verified_email == sample_user.email

        user = get_current_user(db_session, verified_email)
        assert user.id == sample_user.id
        assert user.email == sample_user.email
