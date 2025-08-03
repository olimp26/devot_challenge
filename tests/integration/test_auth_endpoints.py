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
        assert "already exists" in data["detail"]

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


class TestLoginEndpoint:
    """Test the /auth/token (login) endpoint."""

    def test_login_success(self, client, sample_user_data):
        """Test successful login with valid credentials."""
        # Register user first
        register_response = client.post(
            "/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK

        # Login with correct credentials
        login_data = {
            # OAuth2 uses 'username' field
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }

        response = client.post(
            "/auth/token",
            data=login_data,  # form data, not json
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }

        response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    def test_login_invalid_password(self, client, sample_user_data):
        """Test login with correct email but wrong password."""
        # Register user first
        register_response = client.post(
            "/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK

        # Login with wrong password
        login_data = {
            "username": sample_user_data["email"],
            "password": "wrongpassword"
        }

        response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    def test_login_missing_username(self, client):
        """Test login with missing username field."""
        login_data = {
            "password": "somepassword"
        }

        response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_password(self, client):
        """Test login with missing password field."""
        login_data = {
            "username": "test@example.com"
        }

        response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        login_data = {
            "username": "",
            "password": ""
        }

        response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestMeEndpoint:
    """Test the /auth/me endpoint."""

    def test_get_current_user_success(self, client, sample_user_data):
        """Test getting current user info with valid token."""
        # Register and login user
        register_response = client.post(
            "/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK
        user_id = register_response.json()["id"]

        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        login_response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]

        # Get current user info
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == user_id
        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert "created_at" in data
        assert "password" not in data

    def test_get_current_user_no_token(self, client):
        """Test accessing /me endpoint without token."""
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Not authenticated" in data["detail"]

    def test_get_current_user_invalid_token(self, client):
        """Test accessing /me endpoint with invalid token."""
        invalid_token = "invalid.jwt.token"

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid or expired access token" in data["detail"]

    def test_get_current_user_expired_token(self, client, sample_user_data):
        """Test accessing /me endpoint with expired token."""
        from app.core.security import create_access_token
        from datetime import timedelta

        # Create expired token
        expired_token = create_access_token(
            subject=sample_user_data["email"],
            expires_delta=timedelta(minutes=-10)  # Expired 10 minutes ago
        )

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid or expired access token" in data["detail"]

    def test_get_current_user_malformed_header(self, client):
        """Test accessing /me endpoint with malformed Authorization header."""
        malformed_headers = [
            {"Authorization": "InvalidFormat token"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "token_without_bearer_prefix"},
        ]

        for headers in malformed_headers:
            response = client.get("/auth/me", headers=headers)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
