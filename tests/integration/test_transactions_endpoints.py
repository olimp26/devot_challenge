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


class TestTransactionFilters:
    """Test transaction filtering functionality."""

    def test_filter_by_amount_range(self, client, sample_user_data):
        """Test filtering transactions by amount range."""
        token = authenticate_user(client, sample_user_data)
        category_id = create_test_category(client, token)

        # Create transactions with different amounts
        amounts = ["50.00", "100.00", "150.00", "200.00"]
        for i, amount in enumerate(amounts):
            transaction_data = create_test_transaction_data(
                category_id, f"Transaction {i+1}", amount
            )
            client.post(
                "/transactions/",
                json=transaction_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        # Test min_amount filter
        response = client.get(
            "/transactions/?min_amount=100",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 3  # 100, 150, 200
        assert all(float(t["amount"]) >= 100 for t in transactions)

        # Test max_amount filter
        response = client.get(
            "/transactions/?max_amount=150",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 3  # 50, 100, 150
        assert all(float(t["amount"]) <= 150 for t in transactions)

        # Test both min and max amount
        response = client.get(
            "/transactions/?min_amount=100&max_amount=150",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 2  # 100, 150
        assert all(100 <= float(t["amount"]) <= 150 for t in transactions)

    def test_filter_by_date_range(self, client, sample_user_data):
        """Test filtering transactions by date range."""
        token = authenticate_user(client, sample_user_data)
        category_id = create_test_category(client, token)

        # Create transactions with different dates
        dates = ["2025-08-01", "2025-08-05", "2025-08-10", "2025-08-15"]
        for i, date_str in enumerate(dates):
            transaction_data = create_test_transaction_data(
                category_id, f"Transaction {i+1}", "100.00", date_str
            )
            client.post(
                "/transactions/",
                json=transaction_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        # Test from date filter
        response = client.get(
            "/transactions/?from_date=2025-08-05",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 3  # 05, 10, 15
        assert all(t["date"] >= "2025-08-05" for t in transactions)

        # Test to date filter
        response = client.get(
            "/transactions/?to_date=2025-08-10",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 3  # 01, 05, 10
        assert all(t["date"] <= "2025-08-10" for t in transactions)

        # Test both from and to date
        response = client.get(
            "/transactions/?from_date=2025-08-05&to_date=2025-08-10",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 2  # 05, 10
        assert all("2025-08-05" <= t["date"] <=
                   "2025-08-10" for t in transactions)

    def test_filter_by_transaction_type(self, client, sample_user_data):
        """Test filtering transactions by type (income/expense)."""
        token = authenticate_user(client, sample_user_data)

        # Create income and expense categories
        income_category_id = create_test_category(
            client, token, "Salary", "income")
        expense_category_id = create_test_category(
            client, token, "Food", "expense")

        # Create transactions for both types
        income_data = create_test_transaction_data(
            income_category_id, "Salary payment", "2000.00")
        expense_data = create_test_transaction_data(
            expense_category_id, "Grocery shopping", "150.00")

        client.post("/transactions/", json=income_data,
                    headers={"Authorization": f"Bearer {token}"})
        client.post("/transactions/", json=expense_data,
                    headers={"Authorization": f"Bearer {token}"})

        # Test income filter
        response = client.get(
            "/transactions/?category_type=income",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["category_type"] == "income"

        # Test expense filter
        response = client.get(
            "/transactions/?category_type=expense",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["category_type"] == "expense"

    def test_filter_by_description_search(self, client, sample_user_data):
        """Test filtering transactions by description search."""
        token = authenticate_user(client, sample_user_data)
        category_id = create_test_category(client, token)

        # Create transactions with different descriptions
        descriptions = ["Rent payment", "Grocery store",
                        "Gas station", "Rent insurance"]
        for desc in descriptions:
            transaction_data = create_test_transaction_data(
                category_id, desc, "100.00")
            client.post("/transactions/", json=transaction_data,
                        headers={"Authorization": f"Bearer {token}"})

        # Test description search - should find both "Rent payment" and "Rent insurance"
        response = client.get(
            "/transactions/?description_query=rent",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 2
        assert all("rent" in t["description"].lower() for t in transactions)

        # Test case-insensitive search
        response = client.get(
            "/transactions/?description_query=GROCERY",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 1
        assert "grocery" in transactions[0]["description"].lower()

    def test_sorting_functionality(self, client, sample_user_data):
        """Test sorting transactions by different fields."""
        token = authenticate_user(client, sample_user_data)
        category_id = create_test_category(client, token)

        # Create transactions with different amounts and dates
        transactions_data = [
            ("First transaction", "50.00", "2025-08-01"),
            ("Second transaction", "200.00", "2025-08-02"),
            ("Third transaction", "100.00", "2025-08-03")
        ]

        for desc, amount, date_str in transactions_data:
            transaction_data = create_test_transaction_data(
                category_id, desc, amount, date_str)
            client.post("/transactions/", json=transaction_data,
                        headers={"Authorization": f"Bearer {token}"})

        # Test sort by amount ascending
        response = client.get(
            "/transactions/?sort_by=amount&order=asc",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        amounts = [float(t["amount"]) for t in transactions]
        assert amounts == sorted(amounts)

        # Test sort by amount descending
        response = client.get(
            "/transactions/?sort_by=amount&order=desc",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        amounts = [float(t["amount"]) for t in transactions]
        assert amounts == sorted(amounts, reverse=True)

        # Test sort by date ascending
        response = client.get(
            "/transactions/?sort_by=date&order=asc",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        dates = [t["date"] for t in transactions]
        assert dates == sorted(dates)

        # Test sort by description
        response = client.get(
            "/transactions/?sort_by=description&order=asc",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        descriptions = [t["description"] for t in transactions]
        assert descriptions == sorted(descriptions)

    def test_combined_filters(self, client, sample_user_data):
        """Test using multiple filters together."""
        token = authenticate_user(client, sample_user_data)

        # Create different categories
        income_category_id = create_test_category(
            client, token, "Salary", "income")
        expense_category_id = create_test_category(
            client, token, "Food", "expense")

        # Create various transactions
        transactions_data = [
            (income_category_id, "Monthly salary", "3000.00", "2025-08-01"),
            (expense_category_id, "Grocery shopping", "150.00", "2025-08-02"),
            (expense_category_id, "Restaurant dinner", "80.00", "2025-08-03"),
            (income_category_id, "Freelance work", "500.00", "2025-08-04"),
            (expense_category_id, "Gas station", "60.00", "2025-08-05")
        ]

        for cat_id, desc, amount, date_str in transactions_data:
            transaction_data = create_test_transaction_data(
                cat_id, desc, amount, date_str)
            client.post("/transactions/", json=transaction_data,
                        headers={"Authorization": f"Bearer {token}"})

        # Test combined filters: expense type + amount range + date range + description search
        response = client.get(
            "/transactions/?category_type=expense&min_amount=70&max_amount=200&from_date=2025-08-02&to_date=2025-08-04&description_query=shop&sort_by=amount&order=desc",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["description"] == "Grocery shopping"
        assert transactions[0]["category_type"] == "expense"
        assert float(transactions[0]["amount"]) == 150.00
