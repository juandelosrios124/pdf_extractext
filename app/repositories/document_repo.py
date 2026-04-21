# app/repositories/document_repo.py

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class DocumentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["documents"]

    async def save_document(self, filename: str, text: str, checksum: str) -> str:
        document = {
            "filename": filename,
            "text": text,
            "checksum": checksum,    # ← nuevo campo
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_document(self, document_id: str) -> dict | None:
        try:
            object_id = ObjectId(document_id)  # ✅ puede lanzar InvalidId
        except InvalidId:
            return None  # ✅ ID malformado → retornamos None, no explotamos

        result = await self.collection.find_one({"_id": object_id})
        if result:
            result["_id"] = str(result["_id"])
        return result