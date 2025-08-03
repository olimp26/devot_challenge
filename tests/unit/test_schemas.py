import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserLogin, UserResponse


class TestUserSchemas:
    """Test user Pydantic schemas."""

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        data = {
            "email": "valid@example.com",
            "password": "validpassword123",
            "full_name": "Valid User"
        }
        user = UserCreate(**data)

        assert user.email == "valid@example.com"
        assert user.password == "validpassword123"
        assert user.full_name == "Valid User"

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        data = {
            "email": "invalid-email",
            "password": "validpassword123",
            "full_name": "Valid User"
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        assert "value is not a valid email address" in str(exc_info.value)

    def test_user_create_missing_required_fields(self):
        """Test UserCreate with missing required fields."""
        data = {"email": "test@example.com"}

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        assert "Field required" in str(exc_info.value)

    def test_user_login_valid(self):
        """Test UserLogin with valid data."""
        data = {
            "email": "login@example.com",
            "password": "loginpassword"
        }
        user_login = UserLogin(**data)

        assert user_login.email == "login@example.com"
        assert user_login.password == "loginpassword"

    def test_user_response_with_datetime(self):
        """Test UserResponse with datetime field."""
        now = datetime.now()
        data = {
            "id": 1,
            "email": "response@example.com",
            "full_name": "Response User",
            "created_at": now
        }
        user_response = UserResponse(**data)

        assert user_response.id == 1
        assert user_response.created_at == now
