import pytest
from fastapi import status
from decimal import Decimal
from datetime import date
from tests.conftest import authenticate_user, create_test_category, create_test_transaction_data


class TestTransactionEndpoints:
    """Test transaction CRUD operations via API endpoints."""

    def test_create_transaction_authenticated(self, client, sample_user_data):
        """Test creating a transaction when authenticated."""
        token = authenticate_user(client, sample_user_data)

        category_id = create_test_category(client, token)

        transaction_data = create_test_transaction_data(
            category_id, "Test transaction", "99.99", "2025-08-03"
        )
        response = client.post(
            "/transactions/",
            json=transaction_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["category_id"] == category_id
        assert data["description"] == "Test transaction"
        assert data["amount"] == "99.99"
        assert data["date"] == "2025-08-03"
        assert "id" in data
        assert "user_id" in data
        assert "last_changed" in data

    def test_create_transaction_unauthenticated(self, client):
        """Test creating a transaction without authentication should fail."""
        transaction_data = {
            "category_id": 1,
            "description": "Test transaction",
            "amount": "99.99"
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_transaction_with_global_category(self, client, sample_user_data):
        """Test creating a transaction with a global category."""
        token = authenticate_user(client, sample_user_data)

        category_id = create_test_category(
            client, token, "Test Global Category", "income")

        transaction_data = create_test_transaction_data(
            category_id, "Transaction with category", "100.00"
        )
        response = client.post(
            "/transactions/",
            json=transaction_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["category_id"] == category_id

    def test_create_transaction_invalid_category(self, client, sample_user_data):
        """Test creating a transaction with invalid category ID."""
        token = authenticate_user(client, sample_user_data)

        # Create transaction with invalid category
        transaction_data = create_test_transaction_data(
            99999, "Test transaction", "99.99")
        response = client.post(
            "/transactions/",
            json=transaction_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_transactions(self, client, sample_user_data):
        """Test getting transactions for authenticated user."""
        token = authenticate_user(client, sample_user_data)

        category_id = create_test_category(client, token)

        transaction_data = create_test_transaction_data(
            category_id, "Test transaction", "99.99")
        client.post(
            "/transactions/",
            json=transaction_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Get transactions
        response = client.get(
            "/transactions/",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["description"] == "Test transaction"

    def test_get_transactions_unauthenticated(self, client):
        """Test getting transactions without authentication should fail."""
        response = client.get("/transactions/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_transactions_with_category_filter(self, client, sample_user_data):
        """Test filtering transactions by category."""
        token = authenticate_user(client, sample_user_data)

        # Create two categories
        category1_id = create_test_category(
            client, token, "Category 1", "expense")
        category2_id = create_test_category(
            client, token, "Category 2", "income")

        # Create transactions for both categories
        client.post(
            "/transactions/",
            json=create_test_transaction_data(
                category1_id, "Transaction 1", "100.00"),
            headers={"Authorization": f"Bearer {token}"}
        )
        client.post(
            "/transactions/",
            json=create_test_transaction_data(
                category2_id, "Transaction 2", "200.00"),
            headers={"Authorization": f"Bearer {token}"}
        )

        # Filter by category1
        response = client.get(
            f"/transactions/?category_id={category1_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["category_id"] == category1_id

    def test_get_transactions_includes_category_info(self, client, sample_user_data):
        """Test that getting transactions always includes category information."""
        token = authenticate_user(client, sample_user_data)

        category_id = create_test_category(client, token)

        transaction_data = create_test_transaction_data(
            category_id, "Test transaction", "99.99")
        client.post(
            "/transactions/",
            json=transaction_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Get transactions - should always include category info
        response = client.get(
            "/transactions/",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 1
        assert "category_name" in transactions[0]
        assert "category_type" in transactions[0]
        assert transactions[0]["category_name"] == "Test Category"
        assert transactions[0]["category_type"] == "expense"

    def test_update_transaction_success(self, client, sample_user_data):
        """Test updating a transaction successfully."""
        token = authenticate_user(client, sample_user_data)

        category_id = create_test_category(client, token)

        transaction_data = create_test_transaction_data(
            category_id, "Original description", "99.99")
        create_response = client.post(
            "/transactions/",
            json=transaction_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        transaction_id = create_response.json()["id"]

        # Update transaction
        update_data = {
            "description": "Updated description",
            "amount": "150.00"
        }
        response = client.put(
            f"/transactions/{transaction_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["amount"] == "150.00"
        assert data["category_id"] == category_id  # Should remain unchanged

    def test_update_transaction_not_found(self, client, sample_user_data):
        """Test updating a non-existent transaction."""
        token = authenticate_user(client, sample_user_data)

        # Update non-existent transaction
        update_data = {"description": "Updated description"}
        response = client.put(
            "/transactions/99999",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_transaction_success(self, client, sample_user_data):
        """Test deleting a transaction successfully."""
        token = authenticate_user(client, sample_user_data)

        category_id = create_test_category(client, token)

        transaction_data = create_test_transaction_data(
            category_id, "To delete", "99.99")
        create_response = client.post(
            "/transactions/",
            json=transaction_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        transaction_id = create_response.json()["id"]

        # Delete transaction
        response = client.delete(
            f"/transactions/{transaction_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]

        # Verify transaction is deleted
        get_response = client.get(
            f"/transactions/{transaction_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_transaction_not_found(self, client, sample_user_data):
        """Test deleting a non-existent transaction."""
        token = authenticate_user(client, sample_user_data)

        # Delete non-existent transaction
        response = client.delete(
            "/transactions/99999",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
