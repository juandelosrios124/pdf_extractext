# tests/conftest.py

import pytest
import fitz


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Genera un PDF mínimo en memoria para los tests."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((100, 100), "Hola mundo desde el PDF de prueba")
    return doc.tobytes()
