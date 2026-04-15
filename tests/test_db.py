import pytest
from app.db.database import db

@pytest.mark.asyncio
async def test_db_connection():
    await db.connect()

    database = db.get_database()
    result = await database.command("ping")

    assert result["ok"] == 1.0

    await db.disconnect()