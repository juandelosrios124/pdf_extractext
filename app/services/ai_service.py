# app/services/ai_service.py

"""
AI service.

Provides text summarization, question answering, and translation
using a local Ollama instance. Follows the Single Responsibility Principle.
"""

import httpx

from app.core.config import settings


class AIService:
    """
    Service for AI-powered text operations using Ollama.

    All operations communicate with a local Ollama instance
    running the model configured in settings.OLLAMA_MODEL.
    """

    def __init__(self):
        self._base_url = settings.OLLAMA_URL
        self._model = settings.OLLAMA_MODEL

    async def _generate(self, prompt: str) -> str:
        """
        Sends a prompt to Ollama and returns the generated text.

        Args:
            prompt: The complete prompt to send to the model

        Returns:
            Generated text response

        Raises:
            httpx.HTTPError: If the request to Ollama fails
        """
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["response"].strip()

    async def summarize(self, text: str) -> str:
        # Limitar el texto para evitar prompts excesivamente largos
        max_chars = 4000
        truncated_text = text[:max_chars]

        prompt = (
            "Resumí el siguiente texto de forma concisa, "
            "manteniendo solo la información más relevante:\n\n"
            f"{truncated_text}"
        )
        return await self._generate(prompt)

    async def ask(self, context: str, question: str) -> str:
        """
        Answers a question based on the given context.

        Args:
            context: The document text to use as context
            question: The question to answer

        Returns:
            The answer based on the context
        """
        prompt = (
            "Respondé la siguiente pregunta basándote únicamente "
            "en el contexto proporcionado. Si la respuesta no está "
            "en el contexto, decilo explícitamente.\n\n"
            f"Contexto:\n{context}\n\n"
            f"Pregunta: {question}"
        )
        return await self._generate(prompt)

    async def translate(self, text: str, target_language: str) -> str:
        """
        Translates the given text to the target language.

        Args:
            text: The text fragment to translate
            target_language: The language to translate into (e.g. "english")

        Returns:
            The translated text
        """
        prompt = (
            f"Traducí el siguiente texto al {target_language}. "
            "Respondé únicamente con la traducción, sin explicaciones "
            "adicionales:\n\n"
            f"{text}"
        )
        return await self._generate(prompt)