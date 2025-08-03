import pytest
from fastapi import status
from decimal import Decimal
from datetime import date, timedelta

from app.models.category import Category, CategoryType
from tests.conftest import authenticate_user, create_test_category, create_test_transaction_data


class TestSummaryEndpoint:
    """Test the summary endpoint functionality."""

    def test_summary_with_transactions(self, client, db_session):
        """Test summary endpoint with some transactions."""
        # Create test user and get token
        user_data = {
            "email": "summary_user@example.com",
            "password": "testpassword123",
            "full_name": "Summary User"
        }
        token = authenticate_user(client, user_data)

        # Create income category
        income_category_id = create_test_category(
            client, token, "Salary", "income")

        # Create expense category
        expense_category_id = create_test_category(
            client, token, "Food", "expense")

        # Create some transactions
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Income transactions
        income_transaction = create_test_transaction_data(
            income_category_id, "Salary payment", "3000.00", today.isoformat()
        )
        client.post(
            "/transactions/",
            json=income_transaction,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Expense transactions
        expense_transaction = create_test_transaction_data(
            expense_category_id, "Grocery shopping", "150.50", yesterday.isoformat()
        )
        client.post(
            "/transactions/",
            json=expense_transaction,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Get summary
        response = client.get(
            "/summary/",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        summary = response.json()

        # Check structure
        assert "totals" in summary
        assert "category_breakdown" in summary
        assert "metrics" in summary

        # Check totals
        totals = summary["totals"]
        assert Decimal(totals["income"]) == Decimal("3000.00")
        assert Decimal(totals["expense"]) == Decimal("150.50")
        assert Decimal(totals["net"]) == Decimal("2849.50")

        # Check category breakdown
        breakdown = summary["category_breakdown"]
        assert len(breakdown["income"]) == 1
        assert len(breakdown["expense"]) == 1

        # Check income breakdown
        income_breakdown = breakdown["income"][0]
        assert income_breakdown["category"] == "Salary"
        assert Decimal(income_breakdown["total"]) == Decimal("3000.00")

        # Check expense breakdown
        expense_breakdown = breakdown["expense"][0]
        assert expense_breakdown["category"] == "Food"
        assert Decimal(expense_breakdown["total"]) == Decimal("150.50")

    def test_summary_with_date_filters(self, client, db_session):
        """Test summary endpoint with date filters."""
        user_data = {
            "email": "date_filter_user@example.com",
            "password": "testpassword123",
            "full_name": "Date Filter User"
        }
        token = authenticate_user(client, user_data)

        # Create category
        category_id = create_test_category(
            client, token, "Test Income", "income")

        # Create transactions on different dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        # Transaction from a week ago (should be excluded)
        old_transaction = create_test_transaction_data(
            category_id, "Old transaction", "1000.00", week_ago.isoformat()
        )
        client.post(
            "/transactions/",
            json=old_transaction,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Transaction from yesterday (should be included)
        recent_transaction = create_test_transaction_data(
            category_id, "Recent transaction", "500.00", yesterday.isoformat()
        )
        client.post(
            "/transactions/",
            json=recent_transaction,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Get summary with date filter (from yesterday to today)
        response = client.get(
            f"/summary/?from_date={yesterday.isoformat()}&to_date={today.isoformat()}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        summary = response.json()

        # Should only include the recent transaction
        totals = summary["totals"]
        assert Decimal(totals["income"]) == Decimal("500.00")
        assert Decimal(totals["expense"]) == Decimal("0.00")
        assert Decimal(totals["net"]) == Decimal("500.00")

    def test_summary_empty_results(self, client):
        """Test summary endpoint with no transactions."""
        user_data = {
            "email": "empty_user@example.com",
            "password": "testpassword123",
            "full_name": "Empty User"
        }
        token = authenticate_user(client, user_data)

        # Get summary with no transactions
        response = client.get(
            "/summary/",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        summary = response.json()

        # Check empty totals
        totals = summary["totals"]
        assert Decimal(totals["income"]) == Decimal("0.00")
        assert Decimal(totals["expense"]) == Decimal("0.00")
        assert Decimal(totals["net"]) == Decimal("0.00")

        # Check empty breakdowns
        breakdown = summary["category_breakdown"]
        assert len(breakdown["income"]) == 0
        assert len(breakdown["expense"]) == 0

    def test_summary_unauthenticated(self, client):
        """Test summary endpoint without authentication."""
        response = client.get("/summary/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
