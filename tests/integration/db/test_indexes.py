import pytest

from app.repositories.document_repo import DocumentRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_documents_indexes_exist(db):
    indexes = await db[DocumentRepository.collection_name].index_information()

    assert "ux_documents_checksum" in indexes
    assert indexes["ux_documents_checksum"]["unique"] is True

    assert "ix_documents_created_at_desc" in indexes
    assert "ix_documents_filename" in indexes


@pytest.mark.asyncio
@pytest.mark.integration
async def test_users_indexes_exist(db):
    indexes = await db[UserRepository.collection_name].index_information()

    assert "ux_users_email" in indexes
    assert indexes["ux_users_email"]["unique"] is True

    assert "ux_users_username" in indexes
    assert indexes["ux_users_username"]["unique"] is True

    assert "ix_users_created_at_desc" in indexes
