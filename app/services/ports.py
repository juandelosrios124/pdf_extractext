"""Repository ports (Protocolos de dominio).

Puertos de salida (driven ports) que definen el contrato que la capa
de servicios espera de la persistencia, sin acoplarse a una
implementación concreta.
"""

from abc import abstractmethod
from typing import Optional

from app.core.interfaces.repository import RepositoryInterface
from app.models.document import DocumentCreateDocument, DocumentDocument, DocumentUpdateDocument


class DocumentRepositoryPort(
    RepositoryInterface[DocumentDocument, DocumentCreateDocument, DocumentUpdateDocument]
):
    """Puerto de salida para la persistencia de documentos.

    Extiende el contrato CRUD genérico con la operación específica
    del dominio de documentos: búsqueda por checksum (usada para
    detectar duplicados).
    """

    @abstractmethod
    async def find_by_checksum(self, checksum: str) -> Optional[DocumentDocument]:
        """
        Buscar un documento por su checksum SHA-256.

        Args:
            checksum: Checksum del archivo a buscar.

        Returns:
            El documento si existe, None en caso contrario.
        """
        pass