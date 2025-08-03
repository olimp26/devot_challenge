import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        response = client.post("/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be in response

    def test_register_user_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email."""
        # Register user first time
        response1 = client.post("/auth/register", json=sample_user_data)
        assert response1.status_code == status.HTTP_200_OK

        # Try to register with same email
        response2 = client.post("/auth/register", json=sample_user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        data = response2.json()
        assert "Email already registered" in data["detail"]

    def test_register_user_invalid_email(self, client):
        """Test registration with invalid email."""
        invalid_user_data = {
            "email": "invalid-email",
            "password": "validpassword123",
            "full_name": "Invalid Email User"
        }

        response = client.post("/auth/register", json=invalid_user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_data = {
            "email": "incomplete@example.com"
            # Missing password and full_name
        }

        response = client.post("/auth/register", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_empty_password(self, client):
        """Test registration with empty password."""
        data = {
            "email": "empty@example.com",
            "password": "",
            "full_name": "Empty Password User"
        }

        response = client.post("/auth/register", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
