import pytest
from app.services.pdf_service import extract_text_from_bytes

def test_extract_text_returns_string(sample_pdf_bytes):
    result = extract_text_from_bytes(sample_pdf_bytes)
    assert isinstance(result, str)

def test_extract_text_returns_content(sample_pdf_bytes):
    result = extract_text_from_bytes(sample_pdf_bytes)
    assert len(result) > 0

def test_extract_text_with_invalid_bytes_raises_error():
    with pytest.raises(ValueError):
        extract_text_from_bytes(b"esto no es un pdf")