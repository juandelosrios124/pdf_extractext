"""
Base repository.

Abstract base class for all repositories.
Follows the Repository Pattern and Liskov Substitution Principle.
"""

from typing import Generic, TypeVar, Type, Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class.

    Provides common CRUD operations.
    Follows the Template Method pattern for extensibility.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with model class.

        Args:
            model: SQLAlchemy model class
        """
        self._model = model

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Get entity by ID.

        Args:
            session: Database session
            id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        result = await session.execute(select(self._model).where(self._model.id == id))
        return result.scalar_one_or_none()

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get all entities with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities
        """
        result = await session.execute(select(self._model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, obj_in: dict) -> ModelType:
        """
        Create new entity.

        Args:
            session: Database session
            obj_in: Dictionary with entity data

        Returns:
            Created entity
        """
        db_obj = self._model(**obj_in)
        session.add(db_obj)
        await session.flush()
        return db_obj

    async def update(
        self, session: AsyncSession, db_obj: ModelType, obj_in: dict
    ) -> ModelType:
        """
        Update existing entity.

        Args:
            session: Database session
            db_obj: Database entity to update
            obj_in: Dictionary with update data

        Returns:
            Updated entity
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.flush()
        return db_obj

    async def delete(self, session: AsyncSession, db_obj: ModelType) -> None:
        """
        Delete entity.

        Args:
            session: Database session
            db_obj: Entity to delete
        """
        await session.delete(db_obj)
