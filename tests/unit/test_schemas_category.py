import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.models.category import CategoryType


class TestCategorySchemas:
    """Test category Pydantic schemas."""

    def test_category_create_valid(self):
        """Test CategoryCreate with valid data."""
        data = {
            "name": "Groceries",
            "category_type": CategoryType.expense
        }
        category = CategoryCreate(**data)

        assert category.name == "Groceries"
        assert category.category_type == CategoryType.expense

    def test_category_create_valid_income(self):
        """Test CategoryCreate with income type."""
        data = {
            "name": "Salary",
            "category_type": CategoryType.income
        }
        category = CategoryCreate(**data)

        assert category.name == "Salary"
        assert category.category_type == CategoryType.income

    def test_category_create_empty_name(self):
        """Test CategoryCreate with empty name should fail."""
        data = {
            "name": "",
            "category_type": CategoryType.expense
        }

        with pytest.raises(ValidationError) as exc_info:
            CategoryCreate(**data)

        assert "at least 1 character" in str(exc_info.value)

    def test_category_create_long_name(self):
        """Test CategoryCreate with name too long should fail."""
        data = {
            "name": "x" * 101,  # Exceeds 100 character limit
            "category_type": CategoryType.expense
        }

        with pytest.raises(ValidationError) as exc_info:
            CategoryCreate(**data)

        assert "at most 100 characters" in str(exc_info.value)

    def test_category_create_missing_fields(self):
        """Test CategoryCreate with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            CategoryCreate(name="Test")  # Missing category_type

        assert "Field required" in str(exc_info.value)

    def test_category_update_partial(self):
        """Test CategoryUpdate with partial data."""
        # Only updating name
        update_data = CategoryUpdate(name="Updated Name")
        assert update_data.name == "Updated Name"
        assert update_data.category_type is None

        # Only updating category_type
        update_data = CategoryUpdate(category_type=CategoryType.income)
        assert update_data.name is None
        assert update_data.category_type == CategoryType.income

    def test_category_update_all_fields(self):
        """Test CategoryUpdate with all fields."""
        update_data = CategoryUpdate(
            name="Updated Category",
            category_type=CategoryType.income
        )
        assert update_data.name == "Updated Category"
        assert update_data.category_type == CategoryType.income

    def test_category_update_empty(self):
        """Test CategoryUpdate with no fields (should be valid)."""
        update_data = CategoryUpdate()
        assert update_data.name is None
        assert update_data.category_type is None

    def test_category_response_with_user_id(self):
        """Test CategoryResponse with user_id."""
        now = datetime.now()
        data = {
            "id": 1,
            "name": "Test Category",
            "category_type": CategoryType.expense,
            "user_id": 123,
            "last_changed": now
        }
        response = CategoryResponse(**data)

        assert response.id == 1
        assert response.name == "Test Category"
        assert response.category_type == CategoryType.expense
        assert response.user_id == 123
        assert response.last_changed == now

    def test_category_response_global_category(self):
        """Test CategoryResponse for global category (user_id=None)."""
        now = datetime.now()
        data = {
            "id": 1,
            "name": "Global Category",
            "category_type": CategoryType.income,
            "user_id": None,
            "last_changed": now
        }
        response = CategoryResponse(**data)

        assert response.id == 1
        assert response.name == "Global Category"
        assert response.category_type == CategoryType.income
        assert response.user_id is None
        assert response.last_changed == now
