"""Composition root: builds the FastAPI app from explicit settings."""

from fastapi import FastAPI

from extractor.api import health
from extractor.config import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="PDF Extract Service", version="0.1.0")
    app.state.settings = settings
    app.include_router(health.router, prefix="/health", tags=["Health"])
    return app
