<<<<<<< HEAD
# FastAPI MVC Application

A modern FastAPI application following the **Model-View-Controller (MVC)** architecture with **three-layer** structure and **Clean Code** principles.

## Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 3: Presentation                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints (Controllers)                          │  │
│  │  - Handle HTTP requests/responses                     │  │
│  │  - Input validation                                   │  │
│  │  - Dependency injection                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Layer 2: Business Logic                    │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │ Services         │  │ Repositories                      │ │
│  │ - Business rules│  │ - Data access abstraction         │ │
│  │ - Use cases     │  │ - CRUD operations                 │ │
│  │ - Orchestration │  │ - Query logic                     │ │
│  └──────────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Layer 1: Data Access                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Models (SQLAlchemy)                                  │  │
│  │  - Database entities                                  │  │
│  │  - Relationships                                      │  │
│  │  - Constraints                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Clean Code Principles Applied

1. **Meaningful Names**: Intention-revealing names for classes, methods, and variables
2. **Single Responsibility Principle**: Each class has one reason to change
3. **Open/Closed Principle**: Open for extension, closed for modification
4. **Dependency Inversion Principle**: Depend on abstractions, not concretions
5. **Small Functions**: Functions do one thing and do it well
6. **Don't Repeat Yourself (DRY)**: Reusable components and patterns

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   └── users.py          # User endpoints (Controller)
│       ├── __init__.py
│       └── router.py             # API router configuration
├── core/
│   ├── config.py                 # Application configuration
│   ├── exceptions.py             # Custom exceptions
│   ├── logging.py                # Logging setup
│   └── __init__.py
├── db/
│   ├── base.py                   # SQLAlchemy base
│   ├── database.py               # Database connection
│   └── __init__.py
├── models/
│   ├── user.py                   # User model
│   └── __init__.py
├── repositories/
│   ├── base.py                   # Base repository
│   ├── user_repository.py        # User repository
│   └── __init__.py
├── schemas/
│   ├── user.py                   # User schemas (DTOs)
│   └── __init__.py
├── services/
│   ├── user_service.py           # User service (Business logic)
│   └── __init__.py
├── utils/
│   └── __init__.py
├── __init__.py
└── main.py                       # Application entry point

tests/
├── api/                          # API/integration tests
│   ├── test_users.py
│   └── __init__.py
├── unit/                         # Unit tests
│   ├── test_services.py
│   └── __init__.py
├── integration/                  # Integration tests
│   └── __init__.py
├── conftest.py                   # Pytest configuration
└── __init__.py
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip or uv package manager

### Installation

1. **Create virtual environment:**
```bash
# Using uv
uv venv

# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the application:**
```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/users/` | Create user |
| GET | `/api/v1/users/` | List users |
| GET | `/api/v1/users/{id}` | Get user by ID |
| PUT | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_services.py

# Run in verbose mode
pytest -v
```

## Key Design Patterns

### Repository Pattern

```python
# Abstracts data access
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, session, email: str) -> Optional[User]:
        # Implementation
```

### Service Layer Pattern

```python
# Encapsulates business logic
class UserService:
    async def create_user(self, session, user_data: UserCreate) -> UserResponse:
        # Validation
        # Business rules
        # Repository call
        # Return response
```

### Dependency Injection

```python
# FastAPI's dependency injection for clean, testable code
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db_session)
):
    # Implementation
```

## Configuration

Configuration is managed through environment variables with sensible defaults:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | FastAPI MVC Application |
| `APP_VERSION` | Application version | 1.0.0 |
| `DEBUG` | Debug mode | False |
| `DATABASE_URL` | Database connection | sqlite:///./app.db |
| `ALLOWED_HOSTS` | CORS allowed origins | localhost |
| `LOG_LEVEL` | Logging level | INFO |

## Contributing

1. Follow Clean Code principles
2. Write tests for new features
3. Keep functions small and focused
4. Use meaningful, intention-revealing names
5. Maintain separation of concerns

## License

MIT License
=======
# pdf_extractext
Proyecto en el cual podamos extraer un texto de un pdf que es proporcionado por el usuario. Despues se hace un resumen gracias al modelo de IA.

- Python
- UV
- Modelo de IA (a definir)
- Ollama
- Base de datos NO RELACIONAL MongoDB

metodologías:

- TDD
- Proyecto dirigido en Github
- 6 primeros principios de 12 factor API

Principios de programacion:

- Kiss
- Dry
- Yagni
- Solid

Skills:

- clean-code
- TDD
- md

prompt :

- Quiero que me crees una estructura de tres capas, para una aplicación modelo vista controlador, Para ser desarrollada con el framework FastAPI, usando los principios de clean code
>>>>>>> a46ec1e574c3e87b0bf9a251ffa0af16ae7a59ca

## MongoDB Migrations

This project includes a professional migration system for MongoDB.

### Migration System Features

- ✅ Pure async functions as migration units
- ✅ Automatic tracking in MongoDB (`_migration_log` collection)
- ✅ Checksum validation for integrity
- ✅ Distributed locking to prevent concurrent runs
- ✅ Full rollback support (`up` and `down` functions)
- ✅ Dry-run mode for safe testing
- ✅ Migration verification

### Project Structure

```
migrations/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── cli.py               # Command-line interface
├── runner.py            # Migration execution engine
├── registry.py          # Migration tracking
├── config.py            # Configuration
├── exceptions.py        # Custom exceptions
├── logger.py            # Logging utilities
└── versions/            # Migration files
    ├── 001_create_indexes.py
    ├── 002_add_status_field.py
    ├── 003_transform_document_fields.py
    └── 004_add_user_metadata.py
```

### Available Commands

```bash
# Show current status
python -m migrations status

# Execute all pending migrations
python -m migrations migrate

# Preview migrations without executing
python -m migrations migrate --dry-run

# Rollback last migration
python -m migrations rollback

# Rollback specific number of migrations
python -m migrations rollback --steps 3

# Rollback to specific migration
python -m migrations rollback --target 001_create_indexes

# Create new migration
python -m migrations create "add new field"

# Verify migration integrity
python -m migrations verify
```

### Creating a New Migration

```bash
python -m migrations create "add user preferences"
```

This creates a file like `migrations/versions/20240115_143000_add_user_preferences.py`:

```python
"""
Add user preferences

Created: 2024-01-15T14:30:00
"""

migration_id = "20240115_143000_add_user_preferences"
description = "Add user preferences"
created_at = "2024-01-15T14:30:00"
author = "developer"


async def up(db):
    """
    Apply the migration.

    Args:
        db: AsyncIOMotorDatabase instance
    """
    await db.documents.update_many(
        {"preferences": {"$exists": False}},
        {"$set": {"preferences": {}}}
    )


async def down(db):
    """
    Revert the migration.

    Args:
        db: AsyncIOMotorDatabase instance
    """
    await db.documents.update_many(
        {},
        {"$unset": {"preferences": ""}}
    )
```

### Migration Examples

#### 1. Create Indexes

```python
async def up(db):
    await db.documents.create_index("user_id", background=True)

async def down(db):
    await db.documents.drop_index("user_id_1")
```

#### 2. Add Field with Default Value

```python
from datetime import datetime, timezone

async def up(db):
    await db.documents.update_many(
        {"status": {"$exists": False}},
        {"$set": {"status": "pending"}}
    )

async def down(db):
    await db.documents.update_many(
        {},
        {"$unset": {"status": ""}}
    )
```

#### 3. Transform Data Format

```python
async def up(db):
    async for doc in db.documents.find({"metadata": {"$type": "string"}}):
        await db.documents.update_one(
            {"_id": doc["_id"]},
            {"$set": {"metadata": {"value": doc["metadata"]}}}}
        )

async def down(db):
    async for doc in db.documents.find({"metadata.value": {"$exists": True}}):
        await db.documents.update_one(
            {"_id": doc["_id"]},
            {"$set": {"metadata": doc["metadata"]["value"]}}
        )
```

### Best Practices

1. **Always provide down()**: Makes migrations reversible
2. **Use transactions**: For critical data changes
3. **Test in staging**: Run migrations in non-production first
4. **Use --dry-run**: Preview changes before applying
5. **Keep migrations small**: Easier to debug and rollback
6. **Add indexes after data**: Create indexes after data migration
7. **Document changes**: Write clear descriptions

### Environment Variables

```bash
# Enable automatic backups before migration
MIGRATION_CREATE_BACKUPS=true

# Backup directory
MIGRATION_BACKUP_DIR=./migrations/backups

# Dry run mode (simulation only)
MIGRATION_DRY_RUN=false
```
