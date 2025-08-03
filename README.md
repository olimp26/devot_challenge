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

- `POST /auth/register` - Register a new user
- `POST /auth/token` - Login and get access token
- `GET /auth/me` - Get current user information

#### Categories

- `GET /categories/` - List categories (global + user's own when authenticated)
- `POST /categories/` - Create a new category (requires authentication)
- `GET /categories/{id}` - Get specific category
- `PUT /categories/{id}` - Update category (owner only)
- `DELETE /categories/{id}` - Delete category (owner only)
- `GET /categories/?category_type=income|expense` - Filter by category type

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
│   │   └── user.py            # User CRUD operations
│   ├── db/                     # Database configuration
│   │   ├── base.py            # SQLAlchemy base
│   │   └── session.py         # Database session management
│   ├── models/                 # SQLAlchemy models
│   │   ├── category.py        # Category model & CategoryType enum
│   │   └── user.py            # User model
│   ├── routers/                # FastAPI routers
│   │   ├── auth.py            # Authentication endpoints
│   │   └── categories.py      # Category CRUD endpoints
│   ├── schemas/                # Pydantic schemas
│   │   ├── category.py        # Category request/response schemas
│   │   └── user.py            # User request/response schemas
│   └── main.py                 # FastAPI application entry
├── alembic/                    # Database migrations
│   ├── versions/              # Migration scripts
│   │   ├── 7aee8290bba0_initial_migration.py
│   │   ├── fabbd50d85f2_add_categories_table_with_relationships.py
│   │   └── 8917c0b9530b_seed_global_categories.py
│   ├── env.py                 # Alembic configuration
│   └── script.py.mako         # Migration template
├── tests/                      # Test suite
│   ├── integration/           # API endpoint tests
│   ├── unit/                  # Unit tests
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

- **🔐 Authentication**: JWT-based user authentication with HTTPBearer
- **📊 Categories**: CRUD operations with global and user-specific categories
- **🗄️ Database**: SQLite with Alembic migrations
- **🧪 Testing**: Comprehensive unit and integration tests (73 tests)
- **📝 Validation**: Pydantic schemas for request/response validation
- **🏗️ Architecture**: Clean separation of concerns with CRUD, schemas, and routers
- **🔒 Authorization**: User ownership verification for category operations
- **📈 Seeded Data**: Global categories automatically seeded via migrations

## Testing

The project includes comprehensive test coverage with 73 tests across unit and integration testing.

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
```

### Test Structure

- **Unit Tests**: Test individual functions and classes in isolation
  - Database CRUD operations
  - Schema validation
  - Security functions
  - Exception handling
- **Integration Tests**: Test complete API workflows
  - Authentication endpoints
  - Category CRUD endpoints
  - Authorization and access control

## Troubleshooting

### Common Issues

1. **Port already in use**: Stop the container and try again, or change the port mapping in the docker run command
2. **Permission errors**: Ensure Docker has access to the project directory
3. **Database errors**: Make sure migrations have been applied using the alembic commands above
