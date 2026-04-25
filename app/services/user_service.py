"""
User service.

Handles business logic for user operations.
Follows the Single Responsibility Principle.
"""

from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import hash_password
from app.core.exceptions import ConflictException, NotFoundException
from app.schemas.user import UserCreate, UserUpdate, UserResponse


class UserService:
    """
    Service for user management operations.

    Encapsulates business logic for user CRUD operations.
    """

    collection_name = "users"

    def _get_collection(self, session: AsyncIOMotorDatabase):
        return session[self.collection_name]

    def _parse_object_id(self, user_id: str) -> ObjectId:
        try:
            return ObjectId(user_id)
        except InvalidId as exc:
            raise NotFoundException("User not found") from exc

    def _hash_password(self, password: str) -> str:
        return hash_password(password)

    def _to_response(self, document: dict) -> UserResponse:
        return UserResponse(
            id=str(document["_id"]),
            email=document["email"],
            username=document["username"],
            full_name=document.get("full_name"),
            is_active=document["is_active"],
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )

    async def _ensure_unique_constraints(
        self,
        collection,
        *,
        email: Optional[str] = None,
        username: Optional[str] = None,
        exclude_id: Optional[ObjectId] = None,
    ) -> None:
        if email is not None:
            email_filter = {"email": email}
            if exclude_id is not None:
                email_filter["_id"] = {"$ne": exclude_id}
            if await collection.find_one(email_filter):
                raise ConflictException("Email already registered")

        if username is not None:
            username_filter = {"username": username}
            if exclude_id is not None:
                username_filter["_id"] = {"$ne": exclude_id}
            if await collection.find_one(username_filter):
                raise ConflictException("Username already registered")

    async def create_user(
        self, session: AsyncIOMotorDatabase, user_data: UserCreate
    ) -> UserResponse:
        """
        Create a new user.

        Args:
            session: Database session
            user_data: User creation data

        Returns:
            Created user response
        """
        collection = self._get_collection(session)
        await self._ensure_unique_constraints(
            collection, email=user_data.email, username=user_data.username
        )

        now = datetime.now(timezone.utc)
        document = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "hashed_password": self._hash_password(user_data.password),
            "is_active": True,
            "is_superuser": False,
            "created_at": now,
            "updated_at": now,
        }

        result = await collection.insert_one(document)
        document["_id"] = result.inserted_id
        return self._to_response(document)

    async def get_user_by_id(
        self, session: AsyncIOMotorDatabase, user_id: str
    ) -> UserResponse:
        """
        Get user by ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            User response or None if not found
        """
        collection = self._get_collection(session)
        object_id = self._parse_object_id(user_id)
        document = await collection.find_one({"_id": object_id})

        if document is None:
            raise NotFoundException("User not found")

        return self._to_response(document)

    async def list_users(
        self, session: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100
    ) -> List[UserResponse]:
        """
        List users with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of user responses
        """
        collection = self._get_collection(session)
        cursor = collection.find({}).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [self._to_response(document) for document in documents]

    async def update_user(
        self, session: AsyncIOMotorDatabase, user_id: str, user_data: UserUpdate
    ) -> UserResponse:
        """
        Update an existing user.

        Args:
            session: Database session
            user_id: User ID to update
            user_data: Update data

        Returns:
            Updated user response
        """
        collection = self._get_collection(session)
        object_id = self._parse_object_id(user_id)
        existing_user = await collection.find_one({"_id": object_id})

        if existing_user is None:
            raise NotFoundException("User not found")

        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return self._to_response(existing_user)

        await self._ensure_unique_constraints(
            collection,
            email=update_data.get("email"),
            username=update_data.get("username"),
            exclude_id=object_id,
        )

        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(
                update_data.pop("password")
            )

        update_data["updated_at"] = datetime.now(timezone.utc)

        await collection.update_one({"_id": object_id}, {"$set": update_data})
        updated_user = await collection.find_one({"_id": object_id})

        if updated_user is None:
            raise NotFoundException("User not found")

        return self._to_response(updated_user)

    async def delete_user(self, session: AsyncIOMotorDatabase, user_id: str) -> None:
        """
        Delete a user.

        Args:
            session: Database session
            user_id: User ID to delete
        """
        collection = self._get_collection(session)
        object_id = self._parse_object_id(user_id)
        result = await collection.delete_one({"_id": object_id})

        if result.deleted_count == 0:
            raise NotFoundException("User not found")


# Singleton instance
user_service = UserService()
