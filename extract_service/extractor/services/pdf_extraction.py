"""PDF text extraction use case.

SRP: only turns PDF bytes into text and a page count, entirely in memory.
Knows nothing about HTTP.
"""

import logging
from dataclasses import dataclass

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PdfExtraction:
    """Result of extracting a PDF: its full text and number of pages."""

    content: str
    page_count: int


def extract_pdf_content(pdf_bytes: bytes) -> PdfExtraction:
    """Extract text and page count from PDF bytes.

    Raises:
        ValueError: If bytes are not a valid PDF.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except fitz.FileDataError as e:
        logger.warning("Invalid PDF bytes", extra={"pdf_size": len(pdf_bytes)})
        raise ValueError("Invalid PDF bytes provided") from e

    with doc:
        extraction = PdfExtraction(
            content="".join(page.get_text() for page in doc),
            page_count=doc.page_count,
        )

    logger.info(
        "PDF text extraction completed",
        extra={"pages": extraction.page_count, "total_length": len(extraction.content)},
    )
    return extraction
