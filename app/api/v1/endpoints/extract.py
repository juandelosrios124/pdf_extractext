# app/api/v1/endpoints/extract.py

"""Stateless PDF text extraction.

Accepts the PDF either as multipart/form-data (field ``file``) or as the raw
request body. The PDF is kept in memory end to end: the body is read into a
bounded buffer and multipart is parsed in memory instead of through
Starlette's form parser, which spools uploads larger than 1MB to disk.
"""

from email.parser import BytesParser
from email.policy import HTTP
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.concurrency import run_in_threadpool

from app.core.config import settings
from app.schemas.extraction import ExtractResponse
from app.services.pdf_service import extract_pdf_content

MULTIPART_FILE_FIELD = "file"

router = APIRouter()


@router.post(
    "",
    response_model=ExtractResponse,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            MULTIPART_FILE_FIELD: {"type": "string", "format": "binary"}
                        },
                        "required": [MULTIPART_FILE_FIELD],
                    }
                },
                "application/pdf": {"schema": {"type": "string", "format": "binary"}},
            },
        }
    },
)
async def extract_pdf(request: Request) -> ExtractResponse:
    body = await _read_body_within_limit(request, settings.MAX_UPLOAD_SIZE)
    pdf_bytes = _pdf_bytes_from(body, request.headers.get("content-type", ""))

    if not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se recibió ningún PDF",
        )

    try:
        extraction = await run_in_threadpool(extract_pdf_content, pdf_bytes)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido del archivo no es un PDF válido",
        )

    return ExtractResponse(content=extraction.content, page_count=extraction.page_count)


async def _read_body_within_limit(request: Request, max_size: int) -> bytes:
    """Read the request body, aborting as soon as it exceeds ``max_size``."""
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"El archivo supera el tamaño máximo de "
                       f"{max_size // (1024 * 1024)}MB",
            )
    return bytes(body)


def _pdf_bytes_from(body: bytes, content_type: str) -> Optional[bytes]:
    if content_type.startswith("multipart/form-data"):
        return _file_field_from_multipart(body, content_type)
    return body


def _file_field_from_multipart(body: bytes, content_type: str) -> Optional[bytes]:
    headers = f"Content-Type: {content_type}\r\n\r\n".encode("latin-1")
    message = BytesParser(policy=HTTP).parsebytes(headers + body)

    for part in message.iter_parts():
        if part.get_param("name", header="content-disposition") == MULTIPART_FILE_FIELD:
            return part.get_payload(decode=True)
    return None
