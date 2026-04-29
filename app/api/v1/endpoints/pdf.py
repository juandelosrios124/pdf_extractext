# app/api/v1/endpoints/pdf.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.core.config import settings
from app.db.database import db
from app.repositories.document_repo import DocumentRepository
from app.schemas.document import DocumentUploadResponse
from app.services.pdf_service import calculate_checksum, extract_text_from_bytes

router = APIRouter()


def get_document_repository() -> DocumentRepository:
    """Dependency — provee el repository. Fácil de mockear en tests."""
    return DocumentRepository(db=db.get_database())


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    repository: DocumentRepository = Depends(get_document_repository),
):
    # 1️⃣ Validar formato
    if not file.filename.endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un PDF válido"
        )

    pdf_bytes = await file.read()

    # 2️⃣ Validar tamaño
    if len(pdf_bytes) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo de "
                   f"{settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
        )

    # 3️⃣ Calcular checksum
    checksum = calculate_checksum(pdf_bytes)

    # 4️⃣ Verificar duplicado
    existing = await repository.find_by_checksum(checksum)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El documento ya existe en la base de datos "
                   f"con id: {existing['_id']}"
        )

    # 5️⃣ Extraer texto
    try:
        text = extract_text_from_bytes(pdf_bytes)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido del archivo no es un PDF válido"
        )

    # 6️⃣ Persistir
    doc_id = await repository.save_document(file.filename, text, checksum)

    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename,
        checksum=checksum,
        text=text,
    )