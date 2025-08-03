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

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - User login (TODO)
- `GET /auth/me` - Get current user (TODO)

### Example Registration Request

```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "securepassword123",
       "full_name": "John Doe"
     }'
```

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

## Architecture

### Project Structure

```
devot_challenge/
├── app/
│   ├── api/v1/routers/     # API route handlers
│   ├── core/               # Core functionality (security, config)
│   ├── crud/               # Database operations
│   ├── db/                 # Database configuration
│   ├── logger/             # Logging configuration
│   ├── models/             # SQLAlchemy models
│   ├── routers/            # FastAPI routers
│   ├── schemas/            # Pydantic schemas
│   └── main.py             # FastAPI application
├── alembic/                # Database migrations
│   ├── versions/           # Migration scripts
│   └── env.py             # Alembic configuration
├── data/                   # Database files (gitignored)
├── tests/                  # Test suite
├── Dockerfile.stage       # Docker development image
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
└── run.py                 # Application entry point
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Stop the container and try again, or change the port mapping in the docker run command
2. **Permission errors**: Ensure Docker has access to the project directory
3. **Database errors**: Make sure migrations have been applied using the alembic commands above
