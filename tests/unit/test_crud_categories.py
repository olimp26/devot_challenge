import pytest
from app.crud.category import (
    get_categories_for_user,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
    get_categories_by_type
)
from app.models.category import Category, CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate


class TestCategoryCRUD:
    """Test category CRUD operations at the database level."""

    def test_create_category(self, db_session, sample_user):
        """Test creating a category."""
        category_data = CategoryCreate(
            name="Test Category",
            category_type=CategoryType.expense
        )

        category = create_category(db_session, category_data, sample_user.id)

        assert category.id is not None
        assert category.name == "Test Category"
        assert category.category_type == CategoryType.expense
        assert category.user_id == sample_user.id
        assert category.last_changed is not None

    def test_get_categories_for_user_no_auth(self, db_session, sample_user):
        """Test getting categories when not authenticated (only global)."""
        # Create a user category and a global category
        user_category_data = CategoryCreate(
            name="User Category", category_type=CategoryType.expense)
        create_category(db_session, user_category_data, sample_user.id)

        # Create a global category directly
        global_category = Category(
            name="Global Category",
            category_type=CategoryType.income,
            user_id=None
        )
        db_session.add(global_category)
        db_session.commit()

        # Get categories without authentication
        categories = get_categories_for_user(db_session, user_id=None)

        assert len(categories) == 1
        assert categories[0].name == "Global Category"
        assert categories[0].user_id is None

    def test_get_categories_for_user_authenticated(self, db_session, sample_user):
        """Test getting categories when authenticated (global + user's own)."""
        # Create a user category
        user_category_data = CategoryCreate(
            name="User Category", category_type=CategoryType.expense)
        user_category = create_category(
            db_session, user_category_data, sample_user.id)

        # Create a global category
        global_category = Category(
            name="Global Category",
            category_type=CategoryType.income,
            user_id=None
        )
        db_session.add(global_category)
        db_session.commit()

        # Get categories with authentication
        categories = get_categories_for_user(
            db_session, user_id=sample_user.id)

        assert len(categories) == 2
        category_names = [cat.name for cat in categories]
        assert "User Category" in category_names
        assert "Global Category" in category_names

    def test_get_categories_by_type(self, db_session, sample_user):
        """Test filtering categories by type."""
        # Create categories of different types
        income_data = CategoryCreate(
            name="Income Cat", category_type=CategoryType.income)
        expense_data = CategoryCreate(
            name="Expense Cat", category_type=CategoryType.expense)

        create_category(db_session, income_data, sample_user.id)
        create_category(db_session, expense_data, sample_user.id)

        # Get only income categories
        income_categories = get_categories_by_type(
            db_session, "income", sample_user.id)
        assert len(income_categories) == 1
        assert income_categories[0].name == "Income Cat"

        # Get only expense categories
        expense_categories = get_categories_by_type(
            db_session, "expense", sample_user.id)
        assert len(expense_categories) == 1
        assert expense_categories[0].name == "Expense Cat"

    def test_get_category_by_id(self, db_session, sample_user):
        """Test getting a category by ID."""
        category_data = CategoryCreate(
            name="Test Category", category_type=CategoryType.expense)
        created_category = create_category(
            db_session, category_data, sample_user.id)

        # Get category by ID as the owner
        found_category = get_category_by_id(
            db_session, created_category.id, sample_user.id)
        assert found_category is not None
        assert found_category.id == created_category.id
        assert found_category.name == "Test Category"

        # Try to get category by ID as another user (should fail)
        other_user_id = sample_user.id + 999
        found_category = get_category_by_id(
            db_session, created_category.id, other_user_id)
        assert found_category is None

    def test_update_category(self, db_session, sample_user):
        """Test updating a category."""
        # Create category
        category_data = CategoryCreate(
            name="Original Name", category_type=CategoryType.expense)
        created_category = create_category(
            db_session, category_data, sample_user.id)

        # Update category
        update_data = CategoryUpdate(
            name="Updated Name", category_type=CategoryType.income)
        updated_category = update_category(
            db_session, created_category.id, update_data, sample_user.id)

        assert updated_category is not None
        assert updated_category.name == "Updated Name"
        assert updated_category.category_type == CategoryType.income

    def test_update_category_not_owner(self, db_session, sample_user):
        """Test updating a category that doesn't belong to the user."""
        # Create category
        category_data = CategoryCreate(
            name="Original Name", category_type=CategoryType.expense)
        created_category = create_category(
            db_session, category_data, sample_user.id)

        # Try to update with different user ID
        other_user_id = sample_user.id + 999
        update_data = CategoryUpdate(name="Hacked Name")
        updated_category = update_category(
            db_session, created_category.id, update_data, other_user_id)

        assert updated_category is None

    def test_delete_category(self, db_session, sample_user):
        """Test deleting a category."""
        # Create category
        category_data = CategoryCreate(
            name="To Delete", category_type=CategoryType.expense)
        created_category = create_category(
            db_session, category_data, sample_user.id)

        # Delete category
        success = delete_category(
            db_session, created_category.id, sample_user.id)
        assert success is True

        # Verify category is deleted
        found_category = get_category_by_id(
            db_session, created_category.id, sample_user.id)
        assert found_category is None

    def test_delete_category_not_owner(self, db_session, sample_user):
        """Test deleting a category that doesn't belong to the user."""
        # Create category
        category_data = CategoryCreate(
            name="Protected Category", category_type=CategoryType.expense)
        created_category = create_category(
            db_session, category_data, sample_user.id)

        # Try to delete with different user ID
        other_user_id = sample_user.id + 999
        success = delete_category(
            db_session, created_category.id, other_user_id)
        assert success is False

        # Verify category still exists
        found_category = get_category_by_id(
            db_session, created_category.id, sample_user.id)
        assert found_category is not None
