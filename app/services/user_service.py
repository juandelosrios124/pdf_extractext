"""
User service.

Contains user-related business logic.
Follows the Single Responsibility Principle.
"""

from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserUpdate, UserResponse

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """
    User service.

    Handles user-related business logic.
    Acts as an intermediary between controllers and repositories.
    """

    def __init__(self):
        """Initialize user service."""
        self._repository = user_repository

    def _hash_password(self, password: str) -> str:
        """
        Hash a plain text password.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def create_user(
        self, session: AsyncSession, user_create: UserCreate
    ) -> UserResponse:
        """
        Create a new user.

        Args:
            session: Database session
            user_create: User creation data

        Returns:
            Created user

        Raises:
            ConflictException: If email or username already exists
        """
        # Check for existing email
        if await self._repository.exists_by_email(session, user_create.email):
            raise ConflictException(f"Email '{user_create.email}' already registered")

        # Check for existing username
        if await self._repository.exists_by_username(session, user_create.username):
            raise ConflictException(f"Username '{user_create.username}' already taken")

        # Prepare user data
        user_data = user_create.model_dump()
        user_data["hashed_password"] = self._hash_password(user_data.pop("password"))

        # Create user
        user = await self._repository.create(session, user_data)

        return UserResponse.model_validate(user)

    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> UserResponse:
        """
        Get user by ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            User data

        Raises:
            NotFoundException: If user not found
        """
        user = await self._repository.get_by_id(session, user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        return UserResponse.model_validate(user)

    async def get_user_by_email(
        self, session: AsyncSession, email: str
    ) -> Optional[UserResponse]:
        """
        Get user by email.

        Args:
            session: Database session
            email: User email

        Returns:
            User data if found, None otherwise
        """
        user = await self._repository.get_by_email(session, email)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def list_users(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """
        List users with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of users
        """
        users = await self._repository.get_all(session, skip=skip, limit=limit)
        return [UserResponse.model_validate(user) for user in users]

    async def update_user(
        self, session: AsyncSession, user_id: int, user_update: UserUpdate
    ) -> UserResponse:
        """
        Update user.

        Args:
            session: Database session
            user_id: User ID to update
            user_update: Update data

        Returns:
            Updated user

        Raises:
            NotFoundException: If user not found
            ConflictException: If email/username already exists
        """
        # Get existing user
        user = await self._repository.get_by_id(session, user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        update_data = user_update.model_dump(exclude_unset=True)

        # Check for email conflict
        if "email" in update_data:
            existing = await self._repository.get_by_email(
                session, update_data["email"]
            )
            if existing and existing.id != user_id:
                raise ConflictException(
                    f"Email '{update_data['email']}' already registered"
                )

        # Check for username conflict
        if "username" in update_data:
            existing = await self._repository.get_by_username(
                session, update_data["username"]
            )
            if existing and existing.id != user_id:
                raise ConflictException(
                    f"Username '{update_data['username']}' already taken"
                )

        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(
                update_data.pop("password")
            )

        # Update user
        updated_user = await self._repository.update(session, user, update_data)

        return UserResponse.model_validate(updated_user)

    async def delete_user(self, session: AsyncSession, user_id: int) -> None:
        """
        Delete user.

        Args:
            session: Database session
            user_id: User ID to delete

        Raises:
            NotFoundException: If user not found
        """
        user = await self._repository.get_by_id(session, user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")

        await self._repository.delete(session, user)

    async def authenticate_user(
        self, session: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user credentials.

        Args:
            session: Database session
            email: User email
            password: Plain text password

        Returns:
            User if authentication succeeds, None otherwise
        """
        user = await self._repository.get_by_email(session, email)
        if not user:
            return None

        if not self._verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user


# Singleton instance
user_service = UserService()
