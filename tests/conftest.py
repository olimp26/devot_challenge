import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_user(db_session, sample_user_data):
    """Create a sample user in the database for testing."""
    from app.crud.user import create_user
    from app.schemas.user import UserCreate

    user_create = UserCreate(**sample_user_data)
    user = create_user(db_session, user_create)
    return user


@pytest.fixture
def sample_category(db_session, sample_user):
    """Create a sample category for testing."""
    from app.models.category import Category, CategoryType

    category = Category(
        name="Test Category",
        category_type=CategoryType.expense,
        user_id=sample_user.id
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def authenticate_user(client, sample_user_data):
    """Helper function to register and authenticate a user, returning the token."""
    # Register user
    register_response = client.post("/auth/register", json=sample_user_data)
    assert register_response.status_code == 200

    # Login and get token
    login_data = {
        "username": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    login_response = client.post(
        "/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def create_test_category(client, token, name="Test Category", category_type="expense"):
    """Helper function to create a test category, returning the category ID."""
    category_data = {"name": name, "category_type": category_type}
    category_response = client.post(
        "/categories/",
        json=category_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert category_response.status_code == 200
    return category_response.json()["id"]


def create_test_transaction_data(category_id, description="Test transaction", amount="99.99", date=None):
    """Helper function to create transaction data dictionary."""
    data = {
        "category_id": category_id,
        "description": description,
        "amount": amount
    }
    if date:
        data["date"] = date
    return data


def create_transaction_schema(category_id, description="Test transaction", amount="99.99", date=None):
    """Helper function to create TransactionCreate schema object."""
    from app.schemas.transaction import TransactionCreate
    from decimal import Decimal
    from datetime import date as date_type

    data = {
        "category_id": category_id,
        "description": description,
        "amount": Decimal(str(amount))
    }
    if date:
        if isinstance(date, str):
            # Parse string date like "2025-08-03"
            year, month, day = map(int, date.split('-'))
            data["date"] = date_type(year, month, day)
        else:
            data["date"] = date

    return TransactionCreate(**data)
