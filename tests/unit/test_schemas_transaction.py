import pytest
from decimal import Decimal
from datetime import date, datetime
from pydantic import ValidationError

from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse
)


class TestTransactionSchemas:
    """Test transaction Pydantic schemas."""

    def test_transaction_create_valid(self):
        """Test creating a valid transaction."""
        transaction_data = {
            "category_id": 1,
            "description": "Test transaction",
            "amount": Decimal("99.99"),
            "date": date(2025, 8, 3)
        }
        transaction = TransactionCreate(**transaction_data)

        assert transaction.category_id == 1
        assert transaction.description == "Test transaction"
        assert transaction.amount == Decimal("99.99")
        assert transaction.date == date(2025, 8, 3)

    def test_transaction_create_without_date(self):
        """Test creating a transaction without specifying date."""
        transaction_data = {
            "category_id": 1,
            "description": "Test transaction",
            "amount": Decimal("99.99")
        }
        transaction = TransactionCreate(**transaction_data)

        assert transaction.category_id == 1
        assert transaction.description == "Test transaction"
        assert transaction.amount == Decimal("99.99")
        assert transaction.date is None

    def test_transaction_create_negative_amount(self):
        """Test creating a transaction with negative amount should fail."""
        transaction_data = {
            "category_id": 1,
            "description": "Test transaction",
            "amount": Decimal("-50.00")
        }

        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(**transaction_data)

        assert "Amount must be greater than or equal to 0" in str(
            exc_info.value)

    def test_transaction_create_too_many_decimals(self):
        """Test creating a transaction with too many decimal places should fail."""
        transaction_data = {
            "category_id": 1,
            "description": "Test transaction",
            "amount": Decimal("99.999")
        }

        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(**transaction_data)

        assert "Amount can have at most 2 decimal places" in str(
            exc_info.value)

    def test_transaction_create_empty_description(self):
        """Test creating a transaction with empty description should fail."""
        transaction_data = {
            "category_id": 1,
            "description": "",
            "amount": Decimal("99.99")
        }

        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(**transaction_data)

        assert "at least 1 character" in str(exc_info.value)

    def test_transaction_create_long_description(self):
        """Test creating a transaction with too long description should fail."""
        transaction_data = {
            "category_id": 1,
            "description": "x" * 501,
            "amount": Decimal("99.99")
        }

        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(**transaction_data)

        assert "at most 500 characters" in str(exc_info.value)

    def test_transaction_create_missing_required_fields(self):
        """Test creating a transaction without required fields should fail."""
        transaction_data = {
            "description": "Test transaction"
            # Missing category_id and amount
        }

        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(**transaction_data)

        errors = str(exc_info.value)
        assert "category_id" in errors
        assert "amount" in errors

    def test_transaction_update_partial(self):
        """Test partial update of transaction."""
        update_data = {
            "description": "Updated description"
        }
        transaction_update = TransactionUpdate(**update_data)

        assert transaction_update.description == "Updated description"
        assert transaction_update.amount is None
        assert transaction_update.category_id is None
        assert transaction_update.date is None

    def test_transaction_update_all_fields(self):
        """Test updating all fields of transaction."""
        update_data = {
            "category_id": 2,
            "description": "Updated description",
            "amount": Decimal("150.00"),
            "date": date(2025, 8, 4)
        }
        transaction_update = TransactionUpdate(**update_data)

        assert transaction_update.category_id == 2
        assert transaction_update.description == "Updated description"
        assert transaction_update.amount == Decimal("150.00")
        assert transaction_update.date == date(2025, 8, 4)

    def test_transaction_update_negative_amount(self):
        """Test updating with negative amount should fail."""
        update_data = {
            "amount": Decimal("-50.00")
        }

        with pytest.raises(ValidationError) as exc_info:
            TransactionUpdate(**update_data)

        assert "Input should be greater than or equal to 0" in str(
            exc_info.value)

    def test_transaction_update_empty(self):
        """Test empty update should be valid."""
        update_data = {}
        transaction_update = TransactionUpdate(**update_data)

        assert transaction_update.category_id is None
        assert transaction_update.description is None
        assert transaction_update.amount is None
        assert transaction_update.date is None

    def test_transaction_response_with_all_fields(self):
        """Test transaction response schema."""
        response_data = {
            "id": 1,
            "user_id": 1,
            "category_id": 1,
            "description": "Test transaction",
            "amount": Decimal("99.99"),
            "date": date(2025, 8, 3),
            "last_changed": datetime(2025, 8, 3, 12, 0, 0),
            "category_name": "Test Category",
            "category_type": "expense"
        }
        transaction_response = TransactionResponse(**response_data)

        assert transaction_response.id == 1
        assert transaction_response.user_id == 1
        assert transaction_response.category_id == 1
        assert transaction_response.description == "Test transaction"
        assert transaction_response.amount == Decimal("99.99")
        assert transaction_response.date == date(2025, 8, 3)
        assert transaction_response.last_changed == datetime(
            2025, 8, 3, 12, 0, 0)
        assert transaction_response.category_name == "Test Category"
        assert transaction_response.category_type == "expense"

    def test_transaction_response_with_category_info(self):
        """Test transaction response includes category information."""
        response_data = {
            "id": 1,
            "user_id": 1,
            "category_id": 1,
            "description": "Test transaction",
            "amount": Decimal("99.99"),
            "date": date(2025, 8, 3),
            "last_changed": datetime(2025, 8, 3, 12, 0, 0),
            "category_name": "Test Category",
            "category_type": "expense"
        }
        transaction_response = TransactionResponse(**response_data)

        assert transaction_response.id == 1
        assert transaction_response.category_name == "Test Category"
        assert transaction_response.category_type == "expense"

    def test_transaction_amount_precision(self):
        """Test that amounts are handled with correct precision."""
        # Test with 1 decimal place
        transaction_data = {
            "category_id": 1,
            "description": "Test transaction",
            "amount": Decimal("99.9")
        }
        transaction = TransactionCreate(**transaction_data)
        assert transaction.amount == Decimal("99.9")

        # Test with 2 decimal places
        transaction_data["amount"] = Decimal("99.99")
        transaction = TransactionCreate(**transaction_data)
        assert transaction.amount == Decimal("99.99")

        # Test with no decimal places
        transaction_data["amount"] = Decimal("99")
        transaction = TransactionCreate(**transaction_data)
        assert transaction.amount == Decimal("99")
