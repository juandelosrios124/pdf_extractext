import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai_service import AIService


@pytest.fixture
def ai_service():
    return AIService()


@pytest.mark.asyncio
async def test_summarize_returns_string(ai_service):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"response": "Este es un resumen del texto."}
        )
        result = await ai_service.summarize("Texto largo para resumir...")
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_ask_returns_answer_based_on_context(ai_service):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"response": "La respuesta es 42."}
        )
        result = await ai_service.ask(
            context="El sentido de la vida es 42.",
            question="¿Cuál es el sentido de la vida?"
        )
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_translate_returns_translated_text(ai_service):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"response": "Hello world"}
        )
        result = await ai_service.translate("Hola mundo", target_language="english")
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_summarize_raises_error_on_ollama_failure(ai_service):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = Exception("Connection refused")
        with pytest.raises(Exception):
            await ai_service.summarize("Texto de prueba")