# app/services/pdf_service.py

import fitz  # PyMuPDF
import hashlib


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """
    Extrae el texto de un PDF recibido como bytes.
    
    Args:
        pdf_bytes: contenido del PDF en bytes
        
    Returns:
        Texto extraído como string
        
    Raises:
        ValueError: si los bytes no corresponden a un PDF válido
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception:
        raise ValueError("Los bytes proporcionados no corresponden a un PDF válido")

    text = ""
    for page in doc:
        text += page.get_text()

    doc.close()
    return text

def calculate_checksum(file_bytes: bytes) -> str:
    """
    Calcula el checksum SHA-256 de un archivo.

    Args:
        file_bytes: contenido del archivo en bytes

    Returns:
        String hexadecimal de 64 caracteres (SHA-256)
    """
    return hashlib.sha256(file_bytes).hexdigest()
