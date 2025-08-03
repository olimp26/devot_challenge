import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.crud.user import get_user_by_email, create_user
from app.schemas.user import UserCreate


class TestDatabaseConnection:
    """Test database connection and basic operations."""

    def test_database_connection(self, db_session):
        """Test that database connection is working."""
        result = db_session.execute(text("SELECT 1")).scalar()
        assert result == 1

    def test_user_table_creation(self, db_session):
        """Test that user table is created properly."""
        # Try to query the users table
        result = db_session.query(User).count()
        assert result == 0  # Should be empty initially

    def test_database_transaction_rollback(self, db_session):
        """Test database transaction rollback functionality."""
        from app.models.user import User
        from app.core.security import get_password_hash

        # Create user without using CRUD function (to avoid auto-commit)
        hashed_password = get_password_hash("password123")
        user = User(
            email="rollback@test.com",
            full_name="Rollback User",
            hashed_password=hashed_password
        )

        try:
            # Add user to session (but don't commit yet)
            db_session.add(user)

            # Force an error to test rollback
            db_session.execute(text("INVALID SQL"))
            db_session.commit()
        except SQLAlchemyError:
            db_session.rollback()

        # Verify user was rolled back
        found_user = get_user_by_email(db_session, "rollback@test.com")
        assert found_user is None
