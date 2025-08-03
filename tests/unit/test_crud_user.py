import pytest
from datetime import datetime

from app.crud.user import get_user_by_email, create_user
from app.schemas.user import UserCreate
from app.models.user import User


class TestUserCRUD:
    """Test user CRUD operations."""

    def test_create_user(self, db_session):
        """Test creating a new user."""
        user_data = UserCreate(
            email="newuser@example.com",
            password="securepassword123",
            full_name="New User"
        )

        user = create_user(db_session, user_data)

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.hashed_password != "securepassword123"  # Should be hashed
        assert isinstance(user.created_at, datetime)

    def test_get_user_by_email_exists(self, db_session):
        """Test getting user by email when user exists."""
        user_data = UserCreate(
            email="existing@example.com",
            password="password123",
            full_name="Existing User"
        )

        created_user = create_user(db_session, user_data)
        found_user = get_user_by_email(db_session, "existing@example.com")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "existing@example.com"

    def test_get_user_by_email_not_exists(self, db_session):
        """Test getting user by email when user doesn't exist."""
        found_user = get_user_by_email(db_session, "nonexistent@example.com")
        assert found_user is None

    def test_create_user_duplicate_email(self, db_session):
        """Test that creating users with duplicate emails works at CRUD level."""
        user_data1 = UserCreate(
            email="duplicate@example.com",
            password="password1",
            full_name="User One"
        )
        user_data2 = UserCreate(
            email="duplicate@example.com",
            password="password2",
            full_name="User Two"
        )

        # First user should be created successfully
        user1 = create_user(db_session, user_data1)
        assert user1.id is not None

        # Second user with same email should raise database constraint error
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            create_user(db_session, user_data2)
