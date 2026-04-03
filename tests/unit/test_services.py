"""
Unit tests for services.

Tests business logic in isolation.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


@pytest.fixture
def user_service():
    """Provide user service instance."""
    return UserService()


@pytest.mark.asyncio
async def test_create_user_success(user_service, db_session: AsyncSession):
    """Test successful user creation."""
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="securepassword123",
        full_name="Test User",
    )

    result = await user_service.create_user(db_session, user_data)

    assert result.email == "test@example.com"
    assert result.username == "testuser"
    assert result.full_name == "Test User"
    assert result.is_active is True


@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service, db_session: AsyncSession):
    """Test user creation with duplicate email."""
    user_data = UserCreate(
        email="duplicate@example.com", username="user1", password="password123"
    )

    # Create first user
    await user_service.create_user(db_session, user_data)

    # Try to create second user with same email
    user_data2 = UserCreate(
        email="duplicate@example.com", username="user2", password="password456"
    )

    with pytest.raises(ConflictException):
        await user_service.create_user(db_session, user_data2)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service, db_session: AsyncSession):
    """Test getting non-existent user."""
    with pytest.raises(NotFoundException):
        await user_service.get_user_by_id(db_session, 99999)
