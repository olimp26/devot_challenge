import pytest
from fastapi import status


class TestApplication:
    """Test full application integration."""

    def test_user_registration_flow(self, client):
        """Test complete user registration flow."""
        # Step 1: Register a new user
        user_data = {
            "email": "flow@example.com",
            "password": "flowpassword123",
            "full_name": "Flow Test User"
        }

        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK

        user_response = register_response.json()
        assert user_response["email"] == user_data["email"]
        assert user_response["full_name"] == user_data["full_name"]
        assert "id" in user_response

        # Step 2: Verify user cannot be registered again
        duplicate_response = client.post("/auth/register", json=user_data)
        assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST

    def test_multiple_users_registration(self, client):
        """Test registering multiple users."""
        users_data = [
            {
                "email": "user1@example.com",
                "password": "password1",
                "full_name": "User One"
            },
            {
                "email": "user2@example.com",
                "password": "password2",
                "full_name": "User Two"
            },
            {
                "email": "user3@example.com",
                "password": "password3",
                "full_name": "User Three"
            }
        ]

        user_ids = []
        for user_data in users_data:
            response = client.post("/auth/register", json=user_data)
            assert response.status_code == status.HTTP_200_OK

            user_response = response.json()
            user_ids.append(user_response["id"])
            assert user_response["email"] == user_data["email"]

        # Verify all users have unique IDs
        assert len(set(user_ids)) == len(user_ids)

    def test_api_error_handling(self, client):
        """Test API error handling."""
        # Test with completely invalid JSON
        response = client.post(
            "/auth/register",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
