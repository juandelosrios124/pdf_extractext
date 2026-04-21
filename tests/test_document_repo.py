# tests/test_document_repo.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.repositories.document_repo import DocumentRepository

# ✅ ID válido de MongoDB: 24 caracteres hexadecimales
VALID_OBJECT_ID = "507f1f77bcf86cd799439011"

@pytest.fixture
def mock_db():
    db = MagicMock()
    db["documents"].insert_one = AsyncMock(
        return_value=MagicMock(inserted_id=VALID_OBJECT_ID)
    )
    db["documents"].find_one = AsyncMock(
        return_value={
            "_id": VALID_OBJECT_ID,
            "filename": "archivo.pdf",
            "text": "Texto extraído del PDF",
        }
    )
    return db

@pytest.fixture
def repo(mock_db):
    return DocumentRepository(db=mock_db)


@pytest.mark.asyncio
async def test_save_document_returns_id(repo):
    doc_id = await repo.save_document(
        filename="archivo.pdf",
        text="Texto extraído del PDF",
        checksum="abc123def456",
    )
    assert isinstance(doc_id, str)
    assert len(doc_id) > 0


@pytest.mark.asyncio
async def test_save_document_includes_checksum(repo, mock_db):
    await repo.save_document(
        filename="archivo.pdf",
        text="Texto del PDF",
        checksum="abc123def456"
    )
    call_args = mock_db["documents"].insert_one.call_args[0][0]
    assert "checksum" in call_args
    assert call_args["checksum"] == "abc123def456"


@pytest.mark.asyncio
async def test_get_document_returns_dict(repo):
    result = await repo.get_document(VALID_OBJECT_ID)  # ✅ ID válido
    assert result is not None
    assert result["filename"] == "archivo.pdf"
    assert result["text"] == "Texto extraído del PDF"


@pytest.mark.asyncio
async def test_get_document_not_found(repo, mock_db):
    mock_db["documents"].find_one = AsyncMock(return_value=None)
    result = await repo.get_document(VALID_OBJECT_ID)  # ✅ ID válido, resultado None
    assert result is None


# ✅ Nuevo test: qué pasa si el ID tiene formato inválido
@pytest.mark.asyncio
async def test_get_document_with_invalid_id_returns_none(repo):
    result = await repo.get_document("id-malformado")
    assert result is None