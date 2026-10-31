# tests/integration/db/conftest.py

"""Fixtures de la suite de integración contra MongoDB real.

Se seleccionan con `uv run pytest -m integration` (ver README, "Ejecutar tests").
Cada test que usa `db` trabaja sobre una base descartable con las migraciones
reales aplicadas; al terminar se elimina solo esa base.
"""

import re
import uuid

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings
from migrations.runner import MigrationRunner

PING_TIMEOUT_MS = 2000
TEST_DB_PREFIX = "pdf_extract_it_"
PROTECTED_DB_NAMES = {"admin", "local", "config"}


def _redacted_url(url: str) -> str:
    """Oculta usuario y contraseña de la URL para poder mostrarla."""
    return re.sub(r"//[^@/]+@", "//***@", url)


def _assert_disposable(name: str) -> None:
    """Aborta si la base no es inequívocamente una base descartable de tests."""
    if (
        not name.startswith(TEST_DB_PREFIX)
        or name == settings.MONGODB_DB_NAME
        or name in PROTECTED_DB_NAMES
    ):
        pytest.fail(
            f"Abortado: '{name}' no es una base descartable de tests "
            f"(prefijo requerido '{TEST_DB_PREFIX}', "
            f"base configurada '{settings.MONGODB_DB_NAME}').",
            pytrace=False,
        )


@pytest.fixture(scope="session", autouse=True)
def require_mongodb() -> None:
    """Falla rápido y con instrucciones si no hay un MongoDB accesible."""
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=PING_TIMEOUT_MS)
    reason = None
    try:
        client.admin.command("ping")
    except PyMongoError as exc:
        reason = re.split(r", Topology Description| \(configured timeouts", str(exc))[0]
    finally:
        client.close()

    # Fuera del except: así pytest no encadena la traza completa de pymongo.
    if reason is not None:
        pytest.fail(
            f"MongoDB no está disponible en {_redacted_url(settings.MONGODB_URL)} "
            f"(timeout {PING_TIMEOUT_MS} ms): {reason}\n"
            "Los tests de integración necesitan un MongoDB real. Desde la raíz del proyecto:\n"
            "  docker compose up -d mongodb\n"
            "  MONGODB_URL=mongodb://localhost:27017 uv run pytest -m integration",
            pytrace=False,
        )


@pytest.fixture
async def db():
    """Base descartable con las migraciones reales aplicadas; se elimina al terminar."""
    name = f"{TEST_DB_PREFIX}{uuid.uuid4().hex}"
    _assert_disposable(name)

    client = AsyncIOMotorClient(
        settings.MONGODB_URL, serverSelectionTimeoutMS=PING_TIMEOUT_MS
    )
    owned = False
    try:
        if name in await client.list_database_names():
            pytest.fail(
                f"Abortado: la base '{name}' ya existe y no fue creada por este test.",
                pytrace=False,
            )
        owned = True
        database = client[name]
        await MigrationRunner(db=database).migrate()
        yield database
    finally:
        try:
            if owned:
                await client.drop_database(name)
        finally:
            client.close()
