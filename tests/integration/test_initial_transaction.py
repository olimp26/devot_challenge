import pytest
from fastapi import status
from decimal import Decimal

from app.models.category import Category, CategoryType
from app.core.config import get_settings
from tests.conftest import authenticate_user


class TestInitialTransaction:
    """Test the initial transaction feature for new users."""

    def test_new_user_gets_initial_transaction(self, client, db_session):
        """Test that registering a new user creates a initial transaction."""
        # Setup: Create the "Other Income" global category
        other_income_category = Category(
            name="Other Income",
            category_type=CategoryType.income,
            user_id=None  # Global category
        )
        db_session.add(other_income_category)
        db_session.commit()
        db_session.refresh(other_income_category)

        # Register a new user and get token
        user_data = {
            "email": "newuser@example.com",
            "password": "testpassword123",
            "full_name": "New User"
        }
        token = authenticate_user(client, user_data)

        # Check transactions - should have the initial transaction
        transactions_response = client.get(
            "/transactions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert transactions_response.status_code == status.HTTP_200_OK
        transactions = transactions_response.json()

        # Should have exactly 1 transaction (the initial transaction)
        assert len(transactions) == 1

        initial_transaction = transactions[0]
        settings = get_settings()

        # Verify the initial transaction details
        assert initial_transaction["description"] == "Predefined amount of money on account"
        assert Decimal(
            initial_transaction["amount"]) == settings.initial_transaction_amount
        assert initial_transaction["category_id"] == other_income_category.id
        assert initial_transaction["category_name"] == "Other Income"
        assert initial_transaction["category_type"] == "income"

    def test_new_user_without_global_category_no_initial_transaction(self, client):
        """Test that without global 'Other Income' category, no initial transaction is created."""
        # Register a new user without creating the global category first
        user_data = {
            "email": "user_no_initial@example.com",
            "password": "testpassword123",
            "full_name": "No Initial Amount User"
        }
        token = authenticate_user(client, user_data)

        # Check transactions - should have no transactions
        transactions_response = client.get(
            "/transactions/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert transactions_response.status_code == status.HTTP_200_OK
        transactions = transactions_response.json()

        # Should have no transactions
        assert len(transactions) == 0
