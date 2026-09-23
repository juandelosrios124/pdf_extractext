import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ["DEBUG"] = "true"

from app.core.exceptions import ConflictException, NotFoundException
from app.models.document import DocumentDocument
from app.schemas.document import DocumentUpdate
from app.services.document_service import DocumentService

VALID_OBJECT_ID = "507f1f77bcf86cd799439011"
NOW = datetime(2024, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.find_by_checksum = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def document_service(mock_repository) -> DocumentService:
    return DocumentService(mock_repository)


@pytest.fixture
def sample_document() -> DocumentDocument:
    return DocumentDocument(
        id=VALID_OBJECT_ID,
        filename="archivo.pdf",
        text="Texto extraído",
        checksum="abc123sha256",
        created_at=NOW,
        updated_at=NOW,
    )


# --- upload_pdf ---

@pytest.mark.asyncio
async def test_upload_pdf_creates_and_returns_response(document_service, mock_repository):
    mock_repository.create.return_value = DocumentDocument(
        id=VALID_OBJECT_ID,
        filename="archivo.pdf",
        text="Texto extraído",
        checksum="sha256-checksum",
        created_at=NOW,
        updated_at=NOW,
    )

    with (
        patch("app.services.document_service.calculate_checksum", return_value="sha256-checksum"),
        patch("app.services.document_service.extract_text_from_bytes", return_value="Texto extraído"),
    ):
        result = await document_service.upload_pdf(b"%PDF-fake", "archivo.pdf")

    assert result.id == VALID_OBJECT_ID
    assert result.filename == "archivo.pdf"
    assert result.checksum == "sha256-checksum"


@pytest.mark.asyncio
async def test_upload_pdf_raises_conflict_if_duplicate_checksum(document_service, mock_repository):
    mock_repository.find_by_checksum.return_value = DocumentDocument(
        id=VALID_OBJECT_ID,
        filename="archivo.pdf",
        text="Texto",
        checksum="sha256-checksum",
        created_at=NOW,
        updated_at=NOW,
    )

    with (
        patch("app.services.document_service.calculate_checksum", return_value="sha256-checksum"),
        patch("app.services.document_service.extract_text_from_bytes", return_value="Texto"),
    ):
        with pytest.raises(ConflictException, match="ya existe"):
            await document_service.upload_pdf(b"%PDF-fake", "archivo.pdf")


# --- get_document_by_id ---

@pytest.mark.asyncio
async def test_get_document_by_id_returns_response(document_service, mock_repository, sample_document):
    mock_repository.get_by_id.return_value = sample_document

    result = await document_service.get_document_by_id(VALID_OBJECT_ID)

    assert result.id == VALID_OBJECT_ID
    assert result.filename == "archivo.pdf"


@pytest.mark.asyncio
async def test_get_document_by_id_raises_not_found(document_service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await document_service.get_document_by_id(VALID_OBJECT_ID)


# --- list_documents ---

@pytest.mark.asyncio
async def test_list_documents_returns_list(document_service, mock_repository, sample_document):
    mock_repository.get_all.return_value = [sample_document]

    result = await document_service.list_documents()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].filename == "archivo.pdf"


@pytest.mark.asyncio
async def test_list_documents_returns_empty_list(document_service, mock_repository):
    result = await document_service.list_documents()
    assert result == []


# --- update_document ---

@pytest.mark.asyncio
async def test_update_document_returns_updated_response(document_service, mock_repository, sample_document):
    mock_repository.get_by_id.return_value = sample_document
    mock_repository.update.return_value = DocumentDocument(
        id=VALID_OBJECT_ID,
        filename="nuevo.pdf",
        text="Texto",
        checksum="abc123",
        created_at=NOW,
        updated_at=NOW,
    )

    result = await document_service.update_document(
        VALID_OBJECT_ID, DocumentUpdate(filename="nuevo.pdf")
    )

    assert result.filename == "nuevo.pdf"


@pytest.mark.asyncio
async def test_update_document_raises_not_found(document_service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await document_service.update_document(
            VALID_OBJECT_ID, DocumentUpdate(filename="nuevo.pdf")
        )


@pytest.mark.asyncio
async def test_update_document_with_empty_payload_returns_current(
    document_service, mock_repository, sample_document
):
    mock_repository.get_by_id.return_value = sample_document

    result = await document_service.update_document(VALID_OBJECT_ID, DocumentUpdate())

    assert result.filename == "archivo.pdf"
    mock_repository.update.assert_not_called()


# --- delete_document ---

@pytest.mark.asyncio
async def test_delete_document_succeeds(document_service, mock_repository):
    result = await document_service.delete_document(VALID_OBJECT_ID)
    assert result is None


@pytest.mark.asyncio
async def test_delete_document_raises_not_found(document_service, mock_repository):
    mock_repository.delete.return_value = False

    with pytest.raises(NotFoundException):
        await document_service.delete_document(VALID_OBJECT_ID)
