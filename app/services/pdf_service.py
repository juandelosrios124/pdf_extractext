"""PDF text extraction service.

Follows Clean Code principles.
SRP: Only handles PDF text extraction.
"""

import hashlib
from dataclasses import dataclass

import fitz  # PyMuPDF

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class PdfExtraction:
    """Result of extracting a PDF: its full text and number of pages."""

    content: str
    page_count: int


def extract_pdf_content(pdf_bytes: bytes) -> PdfExtraction:
    """Extract text and page count from PDF bytes, entirely in memory.

    Args:
        pdf_bytes: PDF content as bytes.

    Returns:
        The extracted text and the number of pages.

    Raises:
        ValueError: If bytes are not a valid PDF.
    """
    logger.debug("Extracting text from PDF", extra={"pdf_size": len(pdf_bytes)})

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except fitz.FileDataError as e:
        logger.warning(
            "Invalid PDF bytes",
            extra={"pdf_size": len(pdf_bytes), "error": str(e)},
        )
        raise ValueError("Invalid PDF bytes provided") from e

    with doc:
        text_parts = []
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text()
            text_parts.append(page_text)
            logger.debug(
                "Extracted text from page",
                extra={"page": page_num, "text_length": len(page_text)},
            )

    extraction = PdfExtraction(content="".join(text_parts), page_count=len(text_parts))
    logger.info(
        "PDF text extraction completed",
        extra={
            "pages": extraction.page_count,
            "total_length": len(extraction.content),
        },
    )

    return extraction


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes.

    Args:
        pdf_bytes: PDF content as bytes.

    Returns:
        Extracted text.

    Raises:
        ValueError: If bytes are not a valid PDF.
    """
    return extract_pdf_content(pdf_bytes).content


def calculate_checksum(file_bytes: bytes) -> str:
    """
    Calcula el checksum SHA-256 de un archivo.

    Args:
        file_bytes: contenido del archivo en bytes

    Returns:
        String hexadecimal de 64 caracteres (SHA-256)
    """
    return hashlib.sha256(file_bytes).hexdigest()
