# app/api/v1/endpoints/pdf.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.db.database import db
from app.repositories.document_repo import DocumentRepository
from app.schemas.document import DocumentUploadResponse
from app.services.pdf_service import calculate_checksum, extract_text_from_bytes

router = APIRouter()


def get_document_repository() -> DocumentRepository:
    """Dependency — provee el repository. Fácil de mockear en tests."""
    return DocumentRepository(db=db.get_database())


from app.services.pdf_service import calculate_checksum, extract_text_from_bytes

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    repository: DocumentRepository = Depends(get_document_repository),
):
    if not file.filename.endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido")

    pdf_bytes = await file.read()

    # Calcular checksum ANTES de procesar
    checksum = calculate_checksum(pdf_bytes)

    try:
        text = extract_text_from_bytes(pdf_bytes)
    except ValueError:
        raise HTTPException(status_code=400, detail="El contenido del archivo no es un PDF válido")

    doc_id = await repository.save_document(file.filename, text, checksum)

    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename,
        checksum=checksum,
        text=text,
    )