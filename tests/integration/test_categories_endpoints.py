import pytest
from fastapi import status

from app.models.category import CategoryType


class TestCategoriesCRUD:
    """Test category CRUD operations."""

    def test_create_category_authenticated(self, client, sample_user_data):
        """Test creating a category when authenticated."""
        register_response = client.post(
            "/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK

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

        category_data = {
            "name": "Groceries",
            "category_type": "expense"
        }
        response = client.post(
            "/categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Groceries"
        assert data["category_type"] == "expense"
        assert data["user_id"] is not None
        assert "id" in data
        assert "last_changed" in data

    def test_create_category_unauthenticated(self, client):
        """Test creating a category without authentication should fail."""
        category_data = {
            "name": "Groceries",
            "category_type": "expense"
        }
        response = client.post("/categories/", json=category_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_categories_unauthenticated(self, client):
        """Test getting categories without authentication (should only get global ones)."""
        response = client.get("/categories/")
        assert response.status_code == status.HTTP_200_OK
        categories = response.json()
        # Should be empty initially or only contain global categories
        assert isinstance(categories, list)

    def test_get_categories_authenticated(self, client, sample_user_data):
        """Test getting categories when authenticated."""
        # Register user first
        register_response = client.post(
            "/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK

        # Login and create a category
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

        # Create a category
        category_data = {"name": "Groceries", "category_type": "expense"}
        create_response = client.post(
            "/categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == status.HTTP_200_OK

        # Get categories
        response = client.get(
            "/categories/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        categories = response.json()
        assert len(categories) >= 1  # Should include the created category
        # Find the Groceries category we created
        user_categories = [
            cat for cat in categories if cat.get("user_id") is not None]
        assert len(user_categories) == 1
        assert user_categories[0]["name"] == "Groceries"

    def test_get_categories_by_type(self, client, sample_user_data):
        """Test getting categories filtered by type."""
        # Register user first
        register_response = client.post(
            "/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK

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

        # Create categories of different types
        income_category = {"name": "Salary", "category_type": "income"}
        expense_category = {"name": "Groceries", "category_type": "expense"}

        client.post("/categories/", json=income_category,
                    headers={"Authorization": f"Bearer {token}"})
        client.post("/categories/", json=expense_category,
                    headers={"Authorization": f"Bearer {token}"})

        # Get only expense categories
        response = client.get(
            "/categories/?category_type=expense",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        categories = response.json()
        # Filter to only user-created expense categories
        user_expense_categories = [cat for cat in categories if cat.get(
            "user_id") is not None and cat["category_type"] == "expense"]
        assert len(user_expense_categories) == 1
        assert user_expense_categories[0]["category_type"] == "expense"
        assert user_expense_categories[0]["name"] == "Groceries"

    def test_update_category_success(self, client, sample_user_data):
        """Test updating a category successfully."""
        # Register user first
        register_response = client.post(
            "/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_200_OK

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

        # Create category
        category_data = {"name": "Groceries", "category_type": "expense"}
        create_response = client.post(
            "/categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        category_id = create_response.json()["id"]

        # Update category
        update_data = {"name": "Food Shopping"}
        response = client.put(
            f"/categories/{category_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Food Shopping"
        assert data["category_type"] == "expense"  # Should remain unchanged

    def test_update_category_not_owner(self, client, sample_user_data):
        """Test updating a category that doesn't belong to the user."""
        # Create first user and category
        register_response1 = client.post(
            "/auth/register", json=sample_user_data)
        assert register_response1.status_code == status.HTTP_200_OK

        login_data1 = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        login_response1 = client.post(
            "/auth/token",
            data=login_data1,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response1.status_code == status.HTTP_200_OK
        token1 = login_response1.json()["access_token"]

        # Create category with first user
        category_data = {"name": "Groceries", "category_type": "expense"}
        create_response = client.post(
            "/categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        category_id = create_response.json()["id"]

        # Create second user
        user_data2 = {
            "email": "user2@example.com",
            "password": "password123",
            "full_name": "User Two"
        }
        register_response2 = client.post("/auth/register", json=user_data2)
        assert register_response2.status_code == status.HTTP_200_OK

        login_data2 = {
            "username": user_data2["email"],
            "password": user_data2["password"]
        }
        login_response2 = client.post(
            "/auth/token",
            data=login_data2,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response2.status_code == status.HTTP_200_OK
        token2 = login_response2.json()["access_token"]

        # Try to update category with second user
        update_data = {"name": "Hacked Category"}
        response = client.put(
            f"/categories/{category_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_category_success(self, client, sample_user_data):
        """Test deleting a category successfully."""
        # Setup user, token, and category
        register_response = client.post(
            "/auth/register", json=sample_user_data)
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        login_response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]

        # Create category
        category_data = {"name": "Groceries", "category_type": "expense"}
        create_response = client.post(
            "/categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        category_id = create_response.json()["id"]

        # Delete category
        response = client.delete(
            f"/categories/{category_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]

        # Verify category is deleted
        get_response = client.get(
            f"/categories/{category_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_category_not_owner(self, client, sample_user_data):
        """Test deleting a category that doesn't belong to the user."""
        # Similar setup as update test - create category with user1, try to delete with user2
        register_response1 = client.post(
            "/auth/register", json=sample_user_data)
        login_data1 = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        login_response1 = client.post(
            "/auth/token",
            data=login_data1,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token1 = login_response1.json()["access_token"]

        # Create category
        category_data = {"name": "Groceries", "category_type": "expense"}
        create_response = client.post(
            "/categories/",
            json=category_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        category_id = create_response.json()["id"]

        # Create second user
        user_data2 = {
            "email": "user2@example.com",
            "password": "password123",
            "full_name": "User Two"
        }
        register_response2 = client.post("/auth/register", json=user_data2)
        assert register_response2.status_code == status.HTTP_200_OK

        login_data2 = {
            "username": user_data2["email"],
            "password": user_data2["password"]
        }
        login_response2 = client.post(
            "/auth/token",
            data=login_data2,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response2.status_code == status.HTTP_200_OK
        token2 = login_response2.json()["access_token"]

        # Try to delete category with second user
        response = client.delete(
            f"/categories/{category_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
