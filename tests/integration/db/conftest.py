# tests/integration/db/conftest.py

import pytest
from app.db.database import db as mongo_db


@pytest.fixture
async def db():
    """Provee la base Mongo real conectada para los tests de integración de DB."""
    await mongo_db.connect()
    yield mongo_db.get_database()
    await mongo_db.disconnect()
