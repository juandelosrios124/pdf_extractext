"""
Tests for PDF upload endpoint.

Follows the Arrange-Act-Assert pattern.
Uses FastAPI TestClient for integration testing.
"""

import pytest
from datetime import datetime
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.main import create_application


@pytest.fixture
def mock_document_repository():
    """Create a mock DocumentRepository."""
    repo = MagicMock()
    repo.save_document = AsyncMock(return_value="507f1f77bcf86cd799439011")
    return repo


@pytest.fixture
def client(mock_document_repository):
    """Create a test client with mocked dependencies."""
    app = create_application()

    # Override the dependency
    from app.api.v1.endpoints.pdf import get_document_repository

    app.dependency_overrides[get_document_repository] = lambda: mock_document_repository

    return TestClient(app)


class TestPdfUploadEndpoint:
    """Test suite for POST /pdf/upload endpoint."""

    def test_upload_pdf_success(
        self, client, mock_document_repository, sample_pdf_bytes
    ):
        """Test successful PDF upload and text extraction."""
        # Arrange
        mock_document_repository.save_document = AsyncMock(
            return_value="507f1f77bcf86cd799439011"
        )

        # Create multipart form data
        pdf_file = BytesIO(sample_pdf_bytes)

        # Act
        response = client.post(
            "/api/v1/pdf/upload",
            files={"file": ("test_document.pdf", pdf_file, "application/pdf")},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"] == "507f1f77bcf86cd799439011"
        assert "filename" in data
        assert data["filename"] == "test_document.pdf"
        assert "text" in data
        assert "Hola mundo desde el PDF de prueba" in data["text"]

        # Verify repository was called
        mock_document_repository.save_document.assert_called_once()
        call_args = mock_document_repository.save_document.call_args[0]
        assert call_args[0] == "test_document.pdf"
        assert isinstance(call_args[1], str)

    def test_upload_rejects_non_pdf_files(self, client):
        """Test that non-PDF files are rejected with 400."""
        # Arrange
        txt_file = BytesIO(b"This is not a PDF")

        # Act
        response = client.post(
            "/api/v1/pdf/upload",
            files={"file": ("document.txt", txt_file, "text/plain")},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_upload_rejects_invalid_pdf_content(self, client):
        """Test that files with PDF extension but invalid content are rejected."""
        # Arrange - File with .pdf extension but not actual PDF content
        fake_pdf = BytesIO(b"This looks like a PDF but isn't")

        # Act
        response = client.post(
            "/api/v1/pdf/upload",
            files={"file": ("fake.pdf", fake_pdf, "application/pdf")},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_upload_requires_file(self, client):
        """Test that request without file is rejected."""
        # Act
        response = client.post("/api/v1/pdf/upload")

        # Assert
        assert response.status_code == 422
