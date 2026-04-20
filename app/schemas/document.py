# app/schemas/document.py

from pydantic import BaseModel, ConfigDict, Field


class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "filename": "documento.pdf",
                "text": "Contenido del PDF extraído...",
            }
        }
    )

    id: str = Field(..., description="MongoDB document ID")
    filename: str = Field(..., description="Nombre original del archivo PDF")
    text: str = Field(..., description="Texto extraído del PDF")