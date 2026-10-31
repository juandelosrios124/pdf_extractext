# tests/integration/db/test_db_connection.py

import pytest
from app.db.database import db


@pytest.mark.asyncio
@pytest.mark.integration
async def test_db_connection():
    """
    Integration test — requiere MongoDB corriendo.
    Correr con: uv run pytest -m integration (ver README, "Ejecutar tests")
    """
    await db.connect()
    try:
        database = db.get_database()
        result = await database.command("ping")
        assert result["ok"] == 1.0
    finally:
        await db.disconnect()