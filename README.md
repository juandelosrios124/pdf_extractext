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