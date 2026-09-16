# app/api/v1/endpoints/pdf.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.api.deps import get_document_service
from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import get_logger
from app.schemas.document import DocumentResponse, DocumentUpdate
from app.services.document_service import DocumentService
from app.services.ai_service import AIService
from app.schemas.document import DocumentResponse, DocumentUpdate, SummarizeResponse


logger = get_logger(__name__)
router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
):
    if not file.filename.endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un PDF válido",
        )

    pdf_bytes = await file.read()

    if len(pdf_bytes) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo de "
                   f"{settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )

    try:
        return await document_service.upload_pdf(pdf_bytes, file.filename)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido del archivo no es un PDF válido",
        )
    except Exception:
        logger.exception("Error inesperado al subir PDF", extra={"upload_filename": file.filename})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar el PDF",
        )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    document_service: DocumentService = Depends(get_document_service),
):
    return await document_service.list_documents(skip=skip, limit=limit)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        return await document_service.get_document_by_id(document_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    data: DocumentUpdate,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        return await document_service.update_document(document_id, data)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        await document_service.delete_document(document_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

def get_ai_service() -> AIService:
    return AIService()


@router.post("/{document_id}/summarize", response_model=SummarizeResponse)
async def summarize_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
    ai_service: AIService = Depends(get_ai_service),
):
    try:
        summary = await document_service.summarize_document(document_id, ai_service)
        return SummarizeResponse(summary=summary)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))