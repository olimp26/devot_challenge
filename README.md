# DevOT Challenge

A FastAPI-based web application with user authentication and SQLite database.

## Prerequisites

- Docker

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/olimp26/devot_challenge.git
cd devot_challenge
```

### 2. Environment Configuration

```bash
# Copy environment template (if .env.example exists)
cp .env.example .env

# Edit .env file if needed (optional)
# Default settings work out of the box
```

### 3. Build and Run with Docker

```bash
# Build the Docker image
docker build -t devot_challenge:latest -f Dockerfile.stage .

# Run the container
docker run -v ${PWD}:/app -p 8000:8000 devot_challenge:latest
```

### 4. Initialize Database

Apply existing migrations to set up the database:

```bash
# Apply migrations
docker exec -it $(docker ps -q --filter ancestor=devot_challenge:latest) alembic upgrade head
```

The application will be available at: **http://localhost:8000**

### 5. API Documentation

Once running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Available Endpoints

#### Authentication

- `POST /auth/token` - Login with email and password (OAuth2 form)
- `POST /auth/register` - Register new user with email, password and optional full name
- `GET /auth/me` - Get current user information (requires authentication)

#### Categories

- `GET /categories/` - Get all accessible categories (global + user's own when authenticated)
- `GET /categories/{id}` - Get specific category by ID
- `POST /categories/` - Create a new category (requires authentication)
- `PUT /categories/{id}` - Update category (owner only)
- `DELETE /categories/{id}` - Delete category (owner only)
- **Query Parameters**: `?category_type=income|expense` - Filter by category type

#### Transactions

- `GET /transactions/` - Get user's transactions with filtering and pagination
- `GET /transactions/{id}` - Get specific transaction by ID
- `POST /transactions/` - Create a new transaction (requires authentication)
- `PUT /transactions/{id}` - Update transaction (owner only)
- `DELETE /transactions/{id}` - Delete transaction (owner only)
- **Query Parameters**: Support for date range, category filtering, amount filtering, and pagination

#### Summary

- `GET /summary/` - Get financial summary with income, expenses, and balance
- **Query Parameters**: Support for date range filtering to get summary for specific periods

## Database Migrations

This project uses Alembic for database schema management. The initial migration is already included in the repository.

### Common Alembic Commands

```bash
# Apply all pending migrations (run this after cloning)
docker exec -it $(docker ps -q --filter ancestor=devot_challenge:latest) alembic upgrade head

# Check current migration status
docker exec -it $(docker ps -q --filter ancestor=devot_challenge:latest) alembic current

# View migration history
docker exec -it $(docker ps -q --filter ancestor=devot_challenge:latest) alembic history
```

### For Developers: Creating New Migrations

```bash
# After making changes to models, generate a new migration
docker exec -it $(docker ps -q --filter ancestor=devot_challenge:latest) alembic revision --autogenerate -m "Description of changes"

# Apply the new migration
docker exec -it $(docker ps -q --filter ancestor=devot_challenge:latest) alembic upgrade head

# Downgrade to previous migration (if needed)
docker exec -it $(docker ps -q --filter ancestor=devot_challenge:latest) alembic downgrade -1
```

## Database

- **Type**: SQLite
- **Location**: `./data/homebudget.db`
- **Migrations**: Managed with Alembic
- **Current Schema**:
  - `users` - User accounts with authentication
  - `categories` - User-specific and global categories for income/expense tracking
  - `transactions` - Financial transactions linked to users and categories
- **Seeded Data**: Global categories automatically populated via migrations

## Architecture

### Project Structure

```
devot_challenge/
├── app/
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Application configuration
│   │   ├── deps.py            # Dependency injection
│   │   ├── exceptions.py      # Custom exception classes
│   │   ├── logger.py          # Logging configuration
│   │   └── security.py        # Authentication & security
│   ├── crud/                   # Database operations
│   │   ├── category.py        # Category CRUD operations
│   │   ├── transaction.py     # Transaction CRUD operations
│   │   └── user.py            # User CRUD operations
│   ├── db/                     # Database configuration
│   │   ├── base.py            # SQLAlchemy base
│   │   └── session.py         # Database session management
│   ├── models/                 # SQLAlchemy models
│   │   ├── category.py        # Category model & CategoryType enum
│   │   ├── transaction.py     # Transaction model
│   │   └── user.py            # User model
│   ├── routers/                # FastAPI routers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── categories.py      # Category CRUD endpoints
│   │   ├── transactions.py    # Transaction CRUD endpoints
│   │   └── summary.py         # Financial summary endpoints
│   ├── schemas/                # Pydantic schemas
│   │   ├── category.py        # Category request/response schemas
│   │   ├── transaction.py     # Transaction request/response schemas
│   │   ├── summary.py         # Summary request/response schemas
│   │   └── user.py            # User request/response schemas
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py    # Authentication business logic
│   │   ├── category_service.py # Category business logic
│   │   ├── transaction_service.py # Transaction business logic
│   │   ├── summary_service.py # Summary business logic
│   │   └── deps.py            # Service dependency injection
│   └── main.py                 # FastAPI application entry
├── alembic/                    # Database migrations
│   ├── versions/              # Migration scripts
│   │   ├── 7aee8290bba0_initial_migration.py
│   │   ├── fabbd50d85f2_add_categories_table_with_relationships.py
│   │   ├── 8917c0b9530b_seed_global_categories.py
│   │   └── 6209866ebb3e_add_transactions_table.py
│   ├── env.py                 # Alembic configuration
│   └── script.py.mako         # Migration template
├── tests/                      # Test suite
│   ├── integration/           # API endpoint tests
│   │   ├── test_auth_endpoints.py
│   │   ├── test_categories_endpoints.py
│   │   ├── test_transactions_endpoints.py
│   │   ├── test_summary_endpoint.py
│   │   └── test_initial_transaction.py
│   ├── unit/                  # Unit tests
│   │   ├── test_auth_dependencies.py
│   │   ├── test_crud_categories.py
│   │   ├── test_crud_transactions.py
│   │   ├── test_crud_user.py
│   │   ├── test_database.py
│   │   ├── test_exceptions.py
│   │   ├── test_schemas.py
│   │   ├── test_schemas_category.py
│   │   ├── test_schemas_transaction.py
│   │   └── test_security.py
│   └── conftest.py            # Test configuration & fixtures
├── data/                       # Database files (gitignored)
│   └── homebudget.db          # SQLite database
├── .env                        # Environment variables
├── .env.example               # Environment template
├── Dockerfile.stage           # Docker development image
├── alembic.ini               # Alembic configuration
├── requirements.txt           # Python dependencies
├── requirements-dev.txt       # Development dependencies
└── run.py                     # Application entry point
```

### Key Features

- **🔐 Authentication**: JWT-based user authentication with OAuth2PasswordRequestForm
- **📊 Categories**: CRUD operations with global and user-specific categories for income/expense tracking
- **💰 Transactions**: Full transaction management with CRUD operations, filtering, and pagination
- **📈 Financial Summary**: Get income, expense, and balance summaries with date filtering
- **🗄️ Database**: SQLite with Alembic migrations for schema management
- **🧪 Testing**: Comprehensive test coverage with 16 test files covering unit and integration testing
- **📝 Validation**: Pydantic schemas for request/response validation with proper error handling
- **🏗️ Architecture**: Clean separation of concerns with services, CRUD, schemas, and routers
- **🔒 Authorization**: User ownership verification for all user-specific operations
- **🌱 Seeded Data**: Global categories automatically seeded via migrations
- **🔍 Filtering**: Advanced filtering capabilities for transactions and categories
- **📊 Business Logic**: Dedicated service layer for complex business operations

## Testing

The project includes comprehensive test coverage with 128 tests across unit and integration testing, covering all major functionality including authentication, CRUD operations, business logic, and API endpoints.

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run tests with verbose output
pytest -v


# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only

# Run specific test files
pytest tests/unit/test_auth_dependencies.py
pytest tests/integration/test_transactions_endpoints.py
```

### Test Structure

- **Unit Tests (10 files)**: Test individual functions and classes in isolation

  - `test_auth_dependencies.py` - Authentication dependency injection
  - `test_crud_categories.py` - Category database operations
  - `test_crud_transactions.py` - Transaction database operations
  - `test_crud_user.py` - User database operations
  - `test_database.py` - Database connection and session management
  - `test_exceptions.py` - Custom exception handling
  - `test_schemas.py` - General schema validation
  - `test_schemas_category.py` - Category schema validation
  - `test_schemas_transaction.py` - Transaction schema validation
  - `test_security.py` - Security and authentication functions

- **Integration Tests (5 files)**: Test complete API workflows and endpoint interactions
  - `test_auth_endpoints.py` - Authentication API endpoints
  - `test_categories_endpoints.py` - Category CRUD API endpoints
  - `test_transactions_endpoints.py` - Transaction CRUD API endpoints
  - `test_summary_endpoint.py` - Financial summary API endpoints
  - `test_initial_transaction.py` - Initial transaction setup and validation

## Troubleshooting

### Common Issues

1. **Port already in use**: Stop the container and try again, or change the port mapping in the docker run command
2. **Permission errors**: Ensure Docker has access to the project directory
3. **Database errors**: Make sure migrations have been applied using the alembic commands above
4. **Alembic configuration errors**: Ensure `alembic.ini` exists in the project root (should be included in the repository)
5. **Authentication issues**: Make sure to include the Bearer token in the Authorization header for protected endpoints
6. **Transaction validation errors**: Ensure the category_id exists and belongs to a valid category before creating transactions
