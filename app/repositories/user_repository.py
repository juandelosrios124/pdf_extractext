"""
User repository.

Handles user-specific data access operations.
Follows the Single Responsibility Principle.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    User repository.

    Provides user-specific data access operations.
    Extends BaseRepository with user-specific queries.
    """

    def __init__(self):
        """Initialize user repository."""
        super().__init__(User)

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            session: Database session
            email: User email

        Returns:
            User if found, None otherwise
        """
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(
        self, session: AsyncSession, username: str
    ) -> Optional[User]:
        """
        Get user by username.

        Args:
            session: Database session
            username: User username

        Returns:
            User if found, None otherwise
        """
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def exists_by_email(self, session: AsyncSession, email: str) -> bool:
        """
        Check if user exists by email.

        Args:
            session: Database session
            email: User email

        Returns:
            True if user exists, False otherwise
        """
        result = await session.execute(select(User.id).where(User.email == email))
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, session: AsyncSession, username: str) -> bool:
        """
        Check if user exists by username.

        Args:
            session: Database session
            username: User username

        Returns:
            True if user exists, False otherwise
        """
        result = await session.execute(select(User.id).where(User.username == username))
        return result.scalar_one_or_none() is not None


# Singleton instance
user_repository = UserRepository()
