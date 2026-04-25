"""Authentication service."""

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, decode_access_token, verify_password
from app.schemas.auth import Token
from app.schemas.user import UserResponse


class AuthService:
    """Business logic for authentication and token-based identity."""

    collection_name = "users"

    def _get_collection(self, session: AsyncIOMotorDatabase):
        return session[self.collection_name]

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

    async def authenticate_user(
        self, session: AsyncIOMotorDatabase, identifier: str, password: str
    ) -> UserResponse:
        """Validate credentials using username or email."""
        collection = self._get_collection(session)
        document = await collection.find_one(
            {"$or": [{"email": identifier}, {"username": identifier}]}
        )

        if document is None or not verify_password(password, document["hashed_password"]):
            raise UnauthorizedException("Incorrect username/email or password")

        if not document.get("is_active", True):
            raise UnauthorizedException("Inactive user")

        return self._to_response(document)

    async def login(
        self, session: AsyncIOMotorDatabase, identifier: str, password: str
    ) -> Token:
        """Authenticate a user and return a bearer token."""
        user = await self.authenticate_user(session, identifier, password)
        return Token(access_token=create_access_token(user.id))

    async def get_current_user(
        self, session: AsyncIOMotorDatabase, token: str
    ) -> UserResponse:
        """Resolve a bearer token into the authenticated user."""
        payload = decode_access_token(token)
        try:
            user_id = ObjectId(payload["sub"])
        except InvalidId as exc:
            raise UnauthorizedException("Invalid authentication token") from exc

        collection = self._get_collection(session)
        document = await collection.find_one({"_id": user_id})
        if document is None:
            raise UnauthorizedException("User not found for token")

        if not document.get("is_active", True):
            raise UnauthorizedException("Inactive user")

        return self._to_response(document)


auth_service = AuthService()
