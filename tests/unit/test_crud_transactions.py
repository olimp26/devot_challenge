import pytest
from decimal import Decimal
from datetime import date
from tests.conftest import create_transaction_schema

from app.crud.transaction import (
    get_transactions_for_user,
    get_transaction_by_id,
    create_transaction,
    update_transaction,
    delete_transaction
)
from app.models.transaction import Transaction
from app.models.category import Category, CategoryType
from app.schemas.transaction import TransactionUpdate


class TestTransactionCRUD:
    """Test transaction CRUD operations at the database level."""

    def test_create_transaction(self, db_session, sample_user, sample_category):
        """Test creating a transaction."""
        transaction_data = create_transaction_schema(
            sample_category.id, "Test transaction", "99.99", "2025-08-03"
        )

        transaction = create_transaction(
            db_session, transaction_data, sample_user.id)

        assert transaction is not None
        assert transaction.id is not None
        assert transaction.user_id == sample_user.id
        assert transaction.category_id == sample_category.id
        assert transaction.description == "Test transaction"
        assert transaction.amount == Decimal("99.99")
        assert transaction.date == date(2025, 8, 3)
        assert transaction.last_changed is not None

    def test_create_transaction_with_global_category(self, db_session, sample_user):
        """Test creating a transaction with a global category."""
        # Create a global category
        global_category = Category(
            name="Global Income",
            category_type=CategoryType.income,
            user_id=None  # Global category
        )
        db_session.add(global_category)
        db_session.commit()

        transaction_data = create_transaction_schema(
            global_category.id, "Income from global category", "1000.00"
        )

        transaction = create_transaction(
            db_session, transaction_data, sample_user.id)

        assert transaction is not None
        assert transaction.category_id == global_category.id

    def test_create_transaction_invalid_category(self, db_session, sample_user):
        """Test creating a transaction with invalid category ID."""
        transaction_data = create_transaction_schema(
            99999, "Test transaction", "99.99")

        transaction = create_transaction(
            db_session, transaction_data, sample_user.id)
        assert transaction is None

    def test_create_transaction_other_users_category(self, db_session, sample_user):
        """Test creating a transaction with another user's category."""
        # Create another user's category
        other_user_category = Category(
            name="Other User Category",
            category_type=CategoryType.expense,
            user_id=sample_user.id + 999  # Different user
        )
        db_session.add(other_user_category)
        db_session.commit()

        transaction_data = create_transaction_schema(
            other_user_category.id, "Test transaction", "99.99")

        transaction = create_transaction(
            db_session, transaction_data, sample_user.id)
        assert transaction is None

    def test_get_transactions_for_user(self, db_session, sample_user, sample_category):
        """Test getting all transactions for a user."""
        # Create multiple transactions
        for i in range(3):
            transaction_data = create_transaction_schema(
                sample_category.id, f"Transaction {i+1}", f"{(i+1)*10}.00")
            create_transaction(db_session, transaction_data, sample_user.id)

        transactions = get_transactions_for_user(db_session, sample_user.id)

        assert len(transactions) == 3
        assert all(t.user_id == sample_user.id for t in transactions)

    def test_get_transactions_for_user_with_category_filter(self, db_session, sample_user):
        """Test filtering transactions by category."""
        # Create two categories
        category1 = Category(
            name="Category 1", category_type=CategoryType.expense, user_id=sample_user.id)
        category2 = Category(
            name="Category 2", category_type=CategoryType.income, user_id=sample_user.id)
        db_session.add_all([category1, category2])
        db_session.commit()

        # Create transactions for both categories
        create_transaction(db_session, create_transaction_schema(
            category1.id, "Transaction 1", "100.00"
        ), sample_user.id)
        create_transaction(db_session, create_transaction_schema(
            category2.id, "Transaction 2", "200.00"
        ), sample_user.id)

        # Filter by category1
        transactions = get_transactions_for_user(
            db_session, sample_user.id, category_id=category1.id)

        assert len(transactions) == 1
        assert transactions[0].category_id == category1.id

    def test_get_transaction_by_id(self, db_session, sample_user, sample_category):
        """Test getting a transaction by ID."""
        # Create a transaction
        transaction_data = create_transaction_schema(
            sample_category.id, "Test transaction", "99.99")
        created_transaction = create_transaction(
            db_session, transaction_data, sample_user.id)

        # Get transaction by ID
        found_transaction = get_transaction_by_id(
            db_session, created_transaction.id, sample_user.id)

        assert found_transaction is not None
        assert found_transaction.id == created_transaction.id
        assert found_transaction.user_id == sample_user.id

    def test_get_transaction_by_id_other_user(self, db_session, sample_user, sample_category):
        """Test getting a transaction by ID as another user (should fail)."""
        # Create a transaction
        transaction_data = create_transaction_schema(
            sample_category.id, "Test transaction", "99.99")
        created_transaction = create_transaction(
            db_session, transaction_data, sample_user.id)

        # Try to get transaction with different user ID
        other_user_id = sample_user.id + 999
        found_transaction = get_transaction_by_id(
            db_session, created_transaction.id, other_user_id)

        assert found_transaction is None

    def test_update_transaction(self, db_session, sample_user, sample_category):
        """Test updating a transaction."""
        # Create a transaction
        transaction_data = create_transaction_schema(
            sample_category.id, "Original description", "99.99")
        created_transaction = create_transaction(
            db_session, transaction_data, sample_user.id)

        # Update transaction
        update_data = TransactionUpdate(
            description="Updated description",
            amount=Decimal("150.00")
        )
        updated_transaction = update_transaction(
            db_session, created_transaction.id, update_data, sample_user.id
        )

        assert updated_transaction is not None
        assert updated_transaction.description == "Updated description"
        assert updated_transaction.amount == Decimal("150.00")
        assert updated_transaction.category_id == sample_category.id  # Unchanged

    def test_update_transaction_not_owner(self, db_session, sample_user, sample_category):
        """Test updating a transaction that doesn't belong to the user."""
        # Create a transaction
        transaction_data = create_transaction_schema(
            sample_category.id, "Test transaction", "99.99")
        created_transaction = create_transaction(
            db_session, transaction_data, sample_user.id)

        # Try to update with different user ID
        other_user_id = sample_user.id + 999
        update_data = TransactionUpdate(description="Hacked description")
        updated_transaction = update_transaction(
            db_session, created_transaction.id, update_data, other_user_id
        )

        assert updated_transaction is None

    def test_delete_transaction(self, db_session, sample_user, sample_category):
        """Test deleting a transaction."""
        # Create a transaction
        transaction_data = create_transaction_schema(
            sample_category.id, "To delete", "99.99")
        created_transaction = create_transaction(
            db_session, transaction_data, sample_user.id)

        # Delete transaction
        success = delete_transaction(
            db_session, created_transaction.id, sample_user.id)
        assert success is True

        # Verify transaction is deleted
        found_transaction = get_transaction_by_id(
            db_session, created_transaction.id, sample_user.id)
        assert found_transaction is None

    def test_delete_transaction_not_owner(self, db_session, sample_user, sample_category):
        """Test deleting a transaction that doesn't belong to the user."""
        # Create a transaction
        transaction_data = create_transaction_schema(
            sample_category.id, "Protected transaction", "99.99")
        created_transaction = create_transaction(
            db_session, transaction_data, sample_user.id)

        # Try to delete with different user ID
        other_user_id = sample_user.id + 999
        success = delete_transaction(
            db_session, created_transaction.id, other_user_id)
        assert success is False

        # Verify transaction still exists
        found_transaction = get_transaction_by_id(
            db_session, created_transaction.id, sample_user.id)
        assert found_transaction is not None

    def test_get_transactions_includes_category_info(self, db_session, sample_user, sample_category):
        """Test that getting transactions always includes category information."""
        # Create a transaction
        transaction_data = create_transaction_schema(
            sample_category.id, "Test transaction", "99.99")
        create_transaction(db_session, transaction_data, sample_user.id)

        # Get transactions - should always include category info
        transactions = get_transactions_for_user(db_session, sample_user.id)

        assert len(transactions) == 1
        assert transactions[0].category is not None
        assert transactions[0].category.id == sample_category.id
        assert transactions[0].category.name == sample_category.name
        # Test the new properties
        assert transactions[0].category_name == sample_category.name
        assert transactions[0].category_type == sample_category.category_type.value


class TestTransactionFiltering:
    """Test transaction filtering in CRUD operations."""

    def test_filter_by_amount_range(self, db_session, sample_user, sample_category):
        """Test filtering transactions by amount range."""
        # Create transactions with different amounts
        amounts = ["50.00", "100.00", "150.00", "200.00"]
        for amount in amounts:
            transaction_data = create_transaction_schema(
                sample_category.id, f"Test {amount}", amount)
            create_transaction(db_session, transaction_data, sample_user.id)

        # Test min_amount filter
        transactions = get_transactions_for_user(
            db_session, sample_user.id, min_amount=Decimal("100.00")
        )
        assert len(transactions) == 3  # 100, 150, 200
        assert all(t.amount >= Decimal("100.00") for t in transactions)

        # Test max_amount filter
        transactions = get_transactions_for_user(
            db_session, sample_user.id, max_amount=Decimal("150.00")
        )
        assert len(transactions) == 3  # 50, 100, 150
        assert all(t.amount <= Decimal("150.00") for t in transactions)

        # Test both min and max amount
        transactions = get_transactions_for_user(
            db_session, sample_user.id,
            min_amount=Decimal("100.00"),
            max_amount=Decimal("150.00")
        )
        assert len(transactions) == 2  # 100, 150
        assert all(Decimal("100.00") <= t.amount <= Decimal("150.00")
                   for t in transactions)

    def test_filter_by_date_range(self, db_session, sample_user, sample_category):
        """Test filtering transactions by date range."""
        # Create transactions with different dates
        dates = [
            date(2025, 8, 1),
            date(2025, 8, 5),
            date(2025, 8, 10),
            date(2025, 8, 15)
        ]
        for test_date in dates:
            transaction_data = create_transaction_schema(
                sample_category.id, f"Test {test_date}", "100.00"
            )
            transaction_data.date = test_date
            create_transaction(db_session, transaction_data, sample_user.id)

        # Test from_date filter
        transactions = get_transactions_for_user(
            db_session, sample_user.id, from_date=date(2025, 8, 5)
        )
        assert len(transactions) == 3  # 05, 10, 15
        assert all(t.date >= date(2025, 8, 5) for t in transactions)

        # Test to_date filter
        transactions = get_transactions_for_user(
            db_session, sample_user.id, to_date=date(2025, 8, 10)
        )
        assert len(transactions) == 3  # 01, 05, 10
        assert all(t.date <= date(2025, 8, 10) for t in transactions)

        # Test both from and to date
        transactions = get_transactions_for_user(
            db_session, sample_user.id,
            from_date=date(2025, 8, 5),
            to_date=date(2025, 8, 10)
        )
        assert len(transactions) == 2  # 05, 10
        assert all(date(2025, 8, 5) <= t.date <= date(2025, 8, 10)
                   for t in transactions)

    def test_filter_by_category_type(self, db_session, sample_user):
        """Test filtering transactions by category type."""
        from app.models.category import Category, CategoryType

        # Create income and expense categories
        income_category = Category(
            name="Salary", category_type=CategoryType.income, user_id=sample_user.id
        )
        expense_category = Category(
            name="Food", category_type=CategoryType.expense, user_id=sample_user.id
        )
        db_session.add_all([income_category, expense_category])
        db_session.commit()

        # Create transactions for both types
        income_data = create_transaction_schema(
            income_category.id, "Salary payment", "2000.00")
        expense_data = create_transaction_schema(
            expense_category.id, "Grocery shopping", "150.00")

        create_transaction(db_session, income_data, sample_user.id)
        create_transaction(db_session, expense_data, sample_user.id)

        # Test income filter
        transactions = get_transactions_for_user(
            db_session, sample_user.id, category_type=CategoryType.income
        )
        assert len(transactions) == 1
        assert transactions[0].category.category_type == CategoryType.income

        # Test expense filter
        transactions = get_transactions_for_user(
            db_session, sample_user.id, category_type=CategoryType.expense
        )
        assert len(transactions) == 1
        assert transactions[0].category.category_type == CategoryType.expense

    def test_filter_by_description_search(self, db_session, sample_user, sample_category):
        """Test filtering transactions by description search."""
        # Create transactions with different descriptions
        descriptions = ["Rent payment", "Grocery store",
                        "Gas station", "Rent insurance"]
        for desc in descriptions:
            transaction_data = create_transaction_schema(
                sample_category.id, desc, "100.00")
            create_transaction(db_session, transaction_data, sample_user.id)

        # Test description search - should find both "Rent payment" and "Rent insurance"
        transactions = get_transactions_for_user(
            db_session, sample_user.id, description_query="rent"
        )
        assert len(transactions) == 2
        assert all("rent" in t.description.lower() for t in transactions)

        # Test case-insensitive search
        transactions = get_transactions_for_user(
            db_session, sample_user.id, description_query="GROCERY"
        )
        assert len(transactions) == 1
        assert "grocery" in transactions[0].description.lower()

    def test_sorting_functionality(self, db_session, sample_user, sample_category):
        """Test sorting transactions by different fields."""
        # Create transactions with different amounts and dates
        transactions_data = [
            ("First transaction", "50.00", date(2025, 8, 3)),
            ("Second transaction", "200.00", date(2025, 8, 1)),
            ("Third transaction", "100.00", date(2025, 8, 2))
        ]

        for desc, amount, test_date in transactions_data:
            transaction_data = create_transaction_schema(
                sample_category.id, desc, amount)
            transaction_data.date = test_date
            create_transaction(db_session, transaction_data, sample_user.id)

        # Test sort by amount ascending
        transactions = get_transactions_for_user(
            db_session, sample_user.id, sort_by="amount", order="asc"
        )
        amounts = [t.amount for t in transactions]
        assert amounts == sorted(amounts)

        # Test sort by amount descending
        transactions = get_transactions_for_user(
            db_session, sample_user.id, sort_by="amount", order="desc"
        )
        amounts = [t.amount for t in transactions]
        assert amounts == sorted(amounts, reverse=True)

        # Test sort by date ascending
        transactions = get_transactions_for_user(
            db_session, sample_user.id, sort_by="date", order="asc"
        )
        dates = [t.date for t in transactions]
        assert dates == sorted(dates)

        # Test sort by description
        transactions = get_transactions_for_user(
            db_session, sample_user.id, sort_by="description", order="asc"
        )
        descriptions = [t.description for t in transactions]
        assert descriptions == sorted(descriptions)
