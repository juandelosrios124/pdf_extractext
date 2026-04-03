"""
Repositories module - Layer 2: Business Logic Layer (Data Access).

Implements the Repository Pattern for data access abstraction.
Follows the Dependency Inversion Principle.
"""

from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository

__all__ = ["BaseRepository", "UserRepository"]
