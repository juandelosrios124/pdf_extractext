"""Índices creados por las migraciones reales en MongoDB.

Se verifican por clave y unicidad, no por nombre: la migración 007 omite crear
un índice si ya existe uno equivalente con otro nombre.
"""

import pytest

from app.repositories.document_repo import DocumentRepository
from app.repositories.user_repository import UserRepository


async def find_index(collection, key: list[tuple[str, int]]) -> dict | None:
    """Devuelve el índice cuya clave coincide exactamente con `key`, o None."""
    indexes = await collection.index_information()
    return next((index for index in indexes.values() if index["key"] == key), None)


async def assert_index(collection, key: list[tuple[str, int]], unique: bool = False) -> None:
    index = await find_index(collection, key)
    assert index is not None, f"{collection.name}: no hay índice sobre {key}"
    if unique:
        assert index.get("unique") is True, f"{collection.name}: el índice {key} no es único"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_documents_indexes_exist(db):
    documents = db[DocumentRepository.collection_name]

    await assert_index(documents, [("checksum", 1)], unique=True)
    await assert_index(documents, [("created_at", -1)])
    await assert_index(documents, [("filename", 1)])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_users_indexes_exist(db):
    users = db[UserRepository.collection_name]

    await assert_index(users, [("email", 1)], unique=True)
    await assert_index(users, [("username", 1)], unique=True)
    await assert_index(users, [("created_at", -1)])
