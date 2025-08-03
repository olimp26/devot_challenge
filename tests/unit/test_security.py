import pytest

from app.core.security import get_password_hash, verify_password


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
