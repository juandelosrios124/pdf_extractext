"""Document service.

Handles business logic for PDF document CRUD operations.
"""

from datetime import datetime, timezone
from typing import List

from app.core.exceptions import ConflictException, NotFoundException
from app.models.document import DocumentCreateDocument, DocumentDocument, DocumentUpdateDocument
from app.services.ports import DocumentRepositoryPort
from app.schemas.document import DocumentResponse, DocumentUpdate
from app.services.pdf_service import calculate_checksum, extract_text_from_bytes
from app.services.ai_service import AIService


class DocumentService:
    """Service for PDF document CRUD operations."""

    def __init__(self, repository: DocumentRepositoryPort):
        self.repository = repository

    def _to_response(self, document: DocumentDocument) -> DocumentResponse:
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            text=document.text,
            checksum=document.checksum,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

    async def upload_pdf(self, file_bytes: bytes, filename: str) -> DocumentResponse:
        checksum = calculate_checksum(file_bytes)
        existing = await self.repository.find_by_checksum(checksum)
        if existing:
            raise ConflictException(
                f"El documento ya existe en la base de datos con id: {existing.id}"
            )

        text = extract_text_from_bytes(file_bytes)

        now = datetime.now(timezone.utc)
        create_doc = DocumentCreateDocument(
            filename=filename,
            text=text,
            checksum=checksum,
            created_at=now,
            updated_at=now,
        )
        created = await self.repository.create(create_doc)
        return self._to_response(created)

    async def get_document_by_id(self, doc_id: str) -> DocumentResponse:
        document = await self.repository.get_by_id(doc_id)
        if document is None:
            raise NotFoundException("Document not found")

        return self._to_response(document)

    async def list_documents(self, skip: int = 0, limit: int = 100) -> List[DocumentResponse]:
        documents = await self.repository.get_all(skip=skip, limit=limit)
        return [self._to_response(doc) for doc in documents]

    async def update_document(self, doc_id: str, data: DocumentUpdate) -> DocumentResponse:
        existing = await self.repository.get_by_id(doc_id)
        if existing is None:
            raise NotFoundException("Document not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return self._to_response(existing)

        update_data["updated_at"] = datetime.now(timezone.utc)
        updated = await self.repository.update(doc_id, DocumentUpdateDocument(**update_data))
        if updated is None:
            raise NotFoundException("Document not found")

        return self._to_response(updated)

    async def delete_document(self, doc_id: str) -> None:
        deleted = await self.repository.delete(doc_id)
        if not deleted:
            raise NotFoundException("Document not found")

    async def summarize_document(self, doc_id: str, ai_service: AIService) -> str:
        document = await self.repository.get_by_id(doc_id)
        
        if document is None:
            raise NotFoundException("Document not found")
        return await ai_service.summarize(document.text)
